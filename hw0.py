#HW0 : Roni Weiss

# Q1
def twoSum(nums: list[int], target: int) -> list[int]:
    # to reach a complexity of o(nlogn) we wil sort the list to a complexity of o(nlogn) then,
    # we will use binary search to find the target - nums[i] in the list to a complexity of o(logn)
    # and we will do so for every element in the list on length o(n)
    # so the total complexity will be o(nlogn) + o(nlogn) = o(nlogn)
    def binarySearch(nums: list[int], target: int):
        down, up = 0, len(nums) - 1
        while down <= up:
            mid = (down + up) >> 1
            if nums[mid] == target:
                return mid
            elif nums[mid] > target:
                up = mid - 1
            else:
                down = mid + 1

        return -1

    # sort the list in o(nlogn) time
    nums.sort()
    for i in range(len(nums)):
        index = binarySearch(nums, target - nums[i])  # o(logn)
        # if the index is valid and not the same as i
        if index != -1 and index != i:
            return [i, index]


# Q2
def profit(prices: list[int]):
    max_profit = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            if prices[j] - prices[i] > profit:
                max_profit = prices[j] - prices[i]
    return max_profit


# Q3
class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node

    def __str__(self):
        return str(self.value)


def read_file(file_path: str) -> Node:
    file = open(file_path, 'r')
    file_content = file.read()
    file_content = file_content.split(';')
    head = Node(file_content[0])
    current = head
    for i in range(1, len(file_content)):
        current.next = Node(file_content[i])
        current = current.next
    return head


def get_length(head: Node) -> int:
    count = 0
    while head:
        count += 1
        head = head.next
    return count


def sort_in_place(head: Node) -> Node:
    length = get_length(head)
    for i in range(length):
        current = head
        for j in range(length - i - 1):
            if current.value > current.next.value:
                current.value, current.next.value = current.next.value, current.value
            current = current.next
    # the time complexity is o(n^2) and the space complexity is o(1) because we are not initializing any new variables
    # or lists
    return head


if __name__ == '__main__':
    nums = [2, 8, 11, 15]
    target = 10
    print(twoSum(nums, target))
    prices = [7, 1, 5, 3, 6, 4]
    print(profit(prices))
