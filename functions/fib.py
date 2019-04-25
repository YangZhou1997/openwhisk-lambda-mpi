def main(args:
    num = args.get("number", "30")
    return {"fibonacci": F(int(num))}
def F(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return F(n-1)+F(n-2)
