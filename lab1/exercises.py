def print_factor(x: int) -> None:
    for i in range(2, x):
        if x % i == 0:
            print(i)


def main() -> None:
    # Exercise 1: Factors
    x = 52633
    for i in range(2, x):
        if x % i == 0:
            print(i)

    # Exercise 2 & 3: Function + list iteration
    l = [52633, 8137, 1024, 999]
    for n in l:
        print(f"Factors of {n}:")
        print_factor(n)


if __name__ == "__main__":
    main()
