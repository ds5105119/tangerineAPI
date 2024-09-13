from random import SystemRandom


def generate_handle():
    """
    1조개의 handle을 생성 시, 핸들이 적어도 하나 이상 겹칠 확률(https://en.wikipedia.org/wiki/Birthday_problem))
    16자의 경우: 2.61036648185 %
    18자의 경우: 0.00183172928 %
    20자의 경우: 0.00000126852 %
    :return: str
    """
    return ''.join(SystemRandom().choice('abcdefghijklmnopqrstuvwxyz1234567890._') for _ in range(18))


if __name__ == "__main__":
    print(generate_handle())
