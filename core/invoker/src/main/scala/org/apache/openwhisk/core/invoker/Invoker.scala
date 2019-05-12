/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.openwhisk.core.invoker


//import java.nio.file.{Files, Paths, StandardOpenOption}
//import java.util.Calendar

import akka.Done
import akka.actor.{Actor, ActorSystem, Cancellable, CoordinatedShutdown, Props}
import akka.stream.ActorMaterializer
import com.typesafe.config.ConfigValueFactory
import kamon.Kamon
import pureconfig.loadConfigOrThrow
import org.apache.openwhisk.common.Https.HttpsConfig
import org.apache.openwhisk.common._
import org.apache.openwhisk.core.{ConfigKeys, WhiskConfig}
import org.apache.openwhisk.core.WhiskConfig._
import org.apache.openwhisk.core.connector.{MessagingProvider, PingMessage}
import org.apache.openwhisk.core.containerpool.ContainerPoolConfig
import org.apache.openwhisk.core.containerpool.IDIPpair
import org.apache.openwhisk.core.entity.{ActivationEntityLimit, ExecManifest, InvokerInstanceId}
import org.apache.openwhisk.core.entity.size._
import org.apache.openwhisk.http.{BasicHttpService, BasicRasService}
import org.apache.openwhisk.spi.SpiLoader
import org.apache.openwhisk.utils.ExecutionContextFactory

import scala.concurrent.duration._
import scala.concurrent.Await
import scala.util.{Failure, Success, Try}

case class CmdLineArgs(uniqueName: Option[String] = None, id: Option[Int] = None, displayedName: Option[String] = None)

object Invoker {

  protected val protocol = loadConfigOrThrow[String]("whisk.invoker.protocol")

  /**
   * An object which records the environment variables required for this component to run.
   */
  def requiredProperties =
    Map(servicePort -> 8080.toString) ++
      ExecManifest.requiredProperties ++
      kafkaHosts ++
      zookeeperHosts ++
      wskApiHost

  def initKamon(instance: Int): Unit = {
    // Replace the hostname of the invoker to the assigned id of the invoker.
    val newKamonConfig = Kamon.config
      .withValue("kamon.environment.host", ConfigValueFactory.fromAnyRef(s"invoker$instance"))
    Kamon.reconfigure(newKamonConfig)
  }

  def main(args: Array[String]): Unit = {
    ConfigMXBean.register()
    Kamon.loadReportersFromConfig()
    implicit val ec = ExecutionContextFactory.makeCachedThreadPoolExecutionContext()
    implicit val actorSystem: ActorSystem =
      ActorSystem(name = "invoker-actor-system", defaultExecutionContext = Some(ec))
    implicit val logger = new AkkaLogging(akka.event.Logging.getLogger(actorSystem, this))
    val poolConfig: ContainerPoolConfig = loadConfigOrThrow[ContainerPoolConfig](ConfigKeys.containerPool)

    // Prepare Kamon shutdown
    CoordinatedShutdown(actorSystem).addTask(CoordinatedShutdown.PhaseActorSystemTerminate, "shutdownKamon") { () =>
      logger.info(this, s"Shutting down Kamon with coordinated shutdown")
      Kamon.stopAllReporters().map(_ => Done)
    }

    // load values for the required properties from the environment
    implicit val config = new WhiskConfig(requiredProperties)

    def abort(message: String) = {
      logger.error(this, message)(TransactionId.invoker)
      actorSystem.terminate()
      Await.result(actorSystem.whenTerminated, 30.seconds)
      sys.exit(1)
    }

    if (!config.isValid) {
      abort("Bad configuration, cannot start.")
    }

    val execManifest = ExecManifest.initialize(config)
    if (execManifest.isFailure) {
      logger.error(this, s"Invalid runtimes manifest: ${execManifest.failed.get}")
      abort("Bad configuration, cannot start.")
    }

    /** Returns Some(s) if the string is not empty with trimmed whitespace, None otherwise. */
    def nonEmptyString(s: String): Option[String] = {
      val trimmed = s.trim
      if (trimmed.nonEmpty) Some(trimmed) else None
    }

    // process command line arguments
    // We accept the command line grammar of:
    // Usage: invoker [options] [<proposedInvokerId>]
    //    --uniqueName <value>   a unique name to dynamically assign Kafka topics from Zookeeper
    //    --displayedName <value> a name to identify this invoker via invoker health protocol
    //    --id <value>     proposed invokerId
    def parse(ls: List[String], c: CmdLineArgs): CmdLineArgs = {
      ls match {
        case "--uniqueName" :: uniqueName :: tail =>
          parse(tail, c.copy(uniqueName = nonEmptyString(uniqueName)))
        case "--displayedName" :: displayedName :: tail =>
          parse(tail, c.copy(displayedName = nonEmptyString(displayedName)))
        case "--id" :: id :: tail if Try(id.toInt).isSuccess =>
          parse(tail, c.copy(id = Some(id.toInt)))
        case Nil => c
        case _   => abort(s"Error processing command line arguments $ls")
      }
    }
    val cmdLineArgs = parse(args.toList, CmdLineArgs())
    logger.info(this, "Command line arguments parsed to yield " + cmdLineArgs)

    val assignedInvokerId = cmdLineArgs match {
      // --id is defined with a valid value, use this id directly.
      case CmdLineArgs(_, Some(id), _) =>
        logger.info(this, s"invokerReg: using proposedInvokerId $id")
        id

      // --uniqueName is defined with a valid value, id is empty, assign an id via zookeeper
      case CmdLineArgs(Some(unique), None, _) =>
        if (config.zookeeperHosts.startsWith(":") || config.zookeeperHosts.endsWith(":")) {
          abort(s"Must provide valid zookeeper host and port to use dynamicId assignment (${config.zookeeperHosts})")
        }
        new InstanceIdAssigner(config.zookeeperHosts).getId(unique)

      case _ => abort(s"Either --id or --uniqueName must be configured with correct values")
    }

    initKamon(assignedInvokerId)

    val topicBaseName = "invoker"
    val topicName = topicBaseName + assignedInvokerId

    val maxMessageBytes = Some(ActivationEntityLimit.MAX_ACTIVATION_LIMIT)
    val invokerInstance =
      InvokerInstanceId(assignedInvokerId, cmdLineArgs.uniqueName, cmdLineArgs.displayedName, poolConfig.userMemory)

    val msgProvider = SpiLoader.get[MessagingProvider]
    if (msgProvider
          .ensureTopic(config, topic = topicName, topicConfig = topicBaseName, maxMessageBytes = maxMessageBytes)
          .isFailure) {
      abort(s"failure during msgProvider.ensureTopic for topic $topicName")
    }
    val producer = msgProvider.getProducer(config, Some(ActivationEntityLimit.MAX_ACTIVATION_LIMIT))


    val invoker = try {
      new InvokerReactive(config, invokerInstance, producer, poolConfig)
    } catch {
      case e: Exception => abort(s"Failed to initialize reactive invoker: ${e.getMessage}")
    }

    case object WorkOnceNow
    case object ScheduledWork
    class MyWorker(initialDelay: FiniteDuration,
                         interval: FiniteDuration,
                         alwaysWait: Boolean,
                         name: String)(implicit logging: Logging, transid: TransactionId)
      extends Actor {
      implicit val ec = context.dispatcher

      var lastSchedule: Option[Cancellable] = None

      val lastActiveIPSetLocal: scala.collection.mutable.Set[IDIPpair] = scala.collection.mutable.Set[IDIPpair]() // storing the activeIPset in last second.

      override def preStart() = {
        if (initialDelay != Duration.Zero) {
          lastSchedule = Some(context.system.scheduler.scheduleOnce(initialDelay, self, ScheduledWork))
        } else {
          self ! ScheduledWork
        }
      }
      override def postStop() = {
        logging.debug(this, s"$name shutdown")
        lastSchedule.foreach(_.cancel())
      }

      def receive = {
        case WorkOnceNow => Try{
          val diffIPs: (scala.collection.mutable.Set[IDIPpair], scala.collection.mutable.Set[IDIPpair]) = invoker.getAddrMap()
          val myinvokerInstance =
            InvokerInstanceId(invokerInstance.instance, invokerInstance.uniqueName,
              invokerInstance.displayedName, invokerInstance.userMemory,
              diffIPs._1.mkString("&"), diffIPs._2.mkString("&"))

//          IDIPpair("", "").loggingIDIP("Invoker.getAddrMap(): " + "rmIPs: "
//            + diffIPs._1.mkString("&") + "; newIPs: " + diffIPs._2.mkString("&"))

          producer.send("health", PingMessage(myinvokerInstance)).andThen {
            case Failure(t) => logger.error(this, s"failed to ping the controller: $t")
          }
        }

        case ScheduledWork =>
          val deadline = interval.fromNow
          Try{
            val diffIPs: (scala.collection.mutable.Set[IDIPpair], scala.collection.mutable.Set[IDIPpair]) = invoker.getAddrMap()
            val myinvokerInstance =
              InvokerInstanceId(invokerInstance.instance, invokerInstance.uniqueName,
                invokerInstance.displayedName, invokerInstance.userMemory,
                diffIPs._1.mkString("&"), diffIPs._2.mkString("&"))

//            IDIPpair("", "").loggingIDIP("Invoker.getAddrMap(): " + "rmIPs: "
//              + diffIPs._1.mkString("&") + "; newIPs: " + diffIPs._2.mkString("&"))

            producer.send("health", PingMessage(myinvokerInstance)).andThen {
              case Failure(t) => logger.error(this, s"failed to ping the controller: $t")
            }
          } match {
            case Success(result) =>
              result onComplete { _ =>
                val timeToWait = if (alwaysWait) interval else deadline.timeLeft.max(Duration.Zero)
                // context might be null here if a PoisonPill is sent while doing computations
                lastSchedule = Option(context).map(_.system.scheduler.scheduleOnce(timeToWait, self, ScheduledWork))
              }

            case Failure(e) =>
              logging.error(name, s"halted because ${e.getMessage}")
          }
      }
    }


    actorSystem.actorOf(Props(new MyWorker(Duration.Zero, 1.seconds, false, "Scheduler")(logging = logger, transid = TransactionId.unknown)))


    val port = config.servicePort.toInt
    val httpsConfig =
      if (Invoker.protocol == "https") Some(loadConfigOrThrow[HttpsConfig]("whisk.invoker.https")) else None

    BasicHttpService.startHttpService(new BasicRasService {}.route, port, httpsConfig)(
      actorSystem,
      ActorMaterializer.create(actorSystem))
  }
}
