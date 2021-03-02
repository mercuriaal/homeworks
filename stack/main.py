class Stack:
    def __init__(self, brackets):
        self.brackets = [bracket for bracket in brackets]

    def isEmpty(self):
        if len(self.brackets) == 0:
            return True
        else:
            return False

    def push(self, element):
        self.brackets.append(element)

    def pop(self):
        return self.brackets.pop()

    def peek(self):
        return self.brackets[-1]

    def size(self):
        return len(self.brackets)


def assert_balance(bracket):
    stacked_bracket = Stack(bracket)
    if stacked_bracket.size() % 2 == 1:
        print('Несбалансированно')
    else:
        round_count = 0
        square_count = 0
        brace_count = 0
        while not stacked_bracket.isEmpty():
            if stacked_bracket.peek() == ')':
                round_count += 1
            elif stacked_bracket.peek() == ']':
                square_count += 1
            elif stacked_bracket.peek() == '}':
                brace_count += 1
            elif stacked_bracket.peek() == '(':
                round_count -= 1
                if round_count < 0:
                    print('Несбалансированно')
                    break
            elif stacked_bracket.peek() == '[':
                square_count -= 1
                if square_count < 0:
                    print('Несбалансированно')
                    break
            elif stacked_bracket.peek() == '{':
                brace_count -= 1
                if brace_count < 0:
                    print('Несбалансированно')
                    break
            stacked_bracket.pop()
        if stacked_bracket.isEmpty():
            print('Сбалансированно')


if __name__ == '__main__':
    assert_balance('(((([{}]))))')
    assert_balance('[([])((([[[]]])))]{()}')
    assert_balance('{{[()]}}')
    assert_balance('}{}')
    assert_balance('{{[(])]}}')
    assert_balance('[[{())}]')
