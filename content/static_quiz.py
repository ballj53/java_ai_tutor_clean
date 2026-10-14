"""
Static Quiz Questions
Same questions for all participants to ensure valid comparison
"""

from dataclasses import dataclass
from typing import List


@dataclass
class QuizQuestion:
    """A quiz question with multiple choice answers"""
    question: str
    options: List[str]
    correct_index: int  # Index of correct answer (0-based)
    explanation: str
    difficulty: int  # 1 (easy) to 5 (hard)


# ArrayList Quiz Questions
ARRAYLIST_QUIZ = [
    QuizQuestion(
        question="A student is confused because they learned that arrays in Java have a strictly fixed size, but an ArrayList seems to be able to accept an infinite number of items. Conceptually, how is this possible?",
        options=[
            "ArrayLists use dynamic memory allocation instead of underlying arrays.",
            "The ArrayList secretly tracks a fixed-size internal array, and whenever it gets full, it builds a larger one and copies everything over.",
            "The ArrayList compresses the items so they always fit.",
            "The operating system increases the physical memory of the original array."
        ],
        correct_index=1,
        explanation="ArrayLists use regular arrays internally and build new ones when they get full.",
        difficulty=1  # Easy - basic concept
    ),

    QuizQuestion(
        question="You are using an ArrayList in your code and you call `list.add('New Data')`. The underlying array happens to be full. As the programmer writing this code, do you need to take any extra steps to ensure the data is added successfully?",
        options=[
            "Yes, you must manually write a `for` loop to copy the old data into a new array before calling `add()`.",
            "Yes, you must manually call a `list.resize()` method before calling `add()`.",
            "No, you don't have to write anything extra; the ArrayList is an abstraction that handles the creation of the new array and the copying automatically behind the scenes.",
            "Yes, you must specify the new capacity of the array inside the `add()` method, such as `add(20, 'New Data')`."
        ],
        correct_index=2,
        explanation="No extra steps are needed. The ArrayList automatically creates a larger array (usually ~1.5x size) and copies all elements to it behind-the-scenes.",
        difficulty=2  # Medium - requires understanding of mechanism
    ),

    QuizQuestion(
        question="The AI tutor highlighted that the copy loop during a resize is an `O(n)` operation. If your ArrayList currently has 1,000 elements and needs to resize, what does `O(n)` physically mean for the computer's processor in this scenario?",
        options=[
            "The processor executes the copy action 1 time, grabbing all 1,000 elements in one chunk.",
            "The processor executes the copy action 1,000 individual times, moving each element one by one.",
            "The processor executes the copy action 1,000 squared (1,000,000) times.",
            "The processor skips the copy action and just renames the original array."
        ],
        correct_index=1,
        explanation="Because the resizing operation is O(n), the number of copies required increases linearly as the number of elements does.",
        difficulty=3  # Medium-hard - requires Big-O knowledge
    ),

    QuizQuestion(
        question="An ArrayList currently has a 'capacity' of 8, and a 'size' of 7. You run a loop that adds 2 more items. Exactly what happens under the hood?",
        options=[
            "The first item is added instantly. For the second item, the ArrayList creates a larger array, copies the 8 items over, and adds the final item.",
            "The ArrayList crashes on the second item because it exceeds the capacity of 8.",
            "Both items are added instantly, and the capacity silently increases to 9.",
            "The ArrayList creates a larger array immediately before adding the first item, just to be safe."
        ],
        correct_index=0,
        explanation="Because 1 slot remains in the underlying array (capacity - size = 1), it has room for the first item and does not need to be resized to add it. However, more room is needed when the system tries to add the second item.",
        difficulty=2  # Medium - specific detail
    ),

    QuizQuestion(
        question="You are writing a program that needs to load exactly 1,000,000 customer records from a database into a brand-new, default ArrayList. Because you didn't define a starting capacity, what is the major performance consequence?",
        options=[
            "The program will crash because a default ArrayList permanently caps its size at 10.",
            "The program will run slowly because the ArrayList will be forced to repeatedly pause, create a new larger internal array, and copy all elements over, dozens of times.",
            "There is no performance consequence because ArrayLists do not use arrays under the hood.",
            "The ArrayList will automatically detect the database size and reserve 1,000,000 slots the very first time `add()` is called."
        ],
        correct_index=1,
        explanation="Because the default starting capacity for an ArrayList is 10 elements, it will need to frequently resize as elements are added to be able to store them all, requiring elements to be copied. To avoid this bottleneck, it's best to initialize it with an estimated capacity.",
        difficulty=4
    )
]


# Recursion Quiz Questions
RECURSION_QUIZ = [
    QuizQuestion(
        question="What is essential for every recursive method?",
        options=[
            "A loop",
            "A base case",
            "Multiple parameters",
            "A return type of int"
        ],
        correct_index=1,
        explanation="Every recursive method MUST have a base case to stop the recursion, otherwise it will run forever and cause a stack overflow.",
        difficulty=1  # Easy - fundamental concept
    ),

    QuizQuestion(
        question="What happens if a recursive method has no base case?",
        options=[
            "It returns 0",
            "It runs forever until stack overflow",
            "It automatically stops after 100 calls",
            "The compiler prevents it"
        ],
        correct_index=1,
        explanation="Without a base case, the method keeps calling itself forever until the call stack runs out of memory (stack overflow).",
        difficulty=2  # Medium - consequence understanding
    ),

    QuizQuestion(
        question="In recursion, where are function calls stored?",
        options=[
            "The heap",
            "The cache",
            "The call stack",
            "The hard drive"
        ],
        correct_index=2,
        explanation="Each recursive call is pushed onto the call stack, which is why too many recursive calls can cause stack overflow.",
        difficulty=3  # Medium-hard - requires memory model knowledge
    ),

    QuizQuestion(
        question="What does factorial(3) return if defined recursively?",
        options=[
            "3",
            "6",
            "9",
            "12"
        ],
        correct_index=1,
        explanation="factorial(3) = 3 * 2 * 1 = 6. The recursive calls compute 3 * factorial(2), where factorial(2) = 2 * 1.",
        difficulty=2  # Medium - tracing execution
    ),

    QuizQuestion(
        question="What is the base case in fibonacci(n)?",
        options=[
            "n == 0",
            "n == 0 or n == 1",
            "n < 0",
            "n == 10"
        ],
        correct_index=1,
        explanation="Fibonacci has two base cases: fib(0) = 0 and fib(1) = 1. These stop the recursion.",
        difficulty=3  # Medium-hard - multiple base cases
    ),

    QuizQuestion(
        question="Compared to iteration, recursion typically uses:",
        options=[
            "Less memory",
            "More memory due to call stack",
            "The same amount of memory",
            "No memory"
        ],
        correct_index=1,
        explanation="Each recursive call uses stack memory. Iteration uses less memory since it doesn't create multiple stack frames.",
        difficulty=4  # Hard - comparative analysis
    ),

    QuizQuestion(
        question="Which problem is naturally suited for recursion?",
        options=[
            "Printing numbers 1 to 100",
            "Traversing a tree structure",
            "Finding the maximum in an array",
            "Swapping two variables"
        ],
        correct_index=1,
        explanation="Tree traversal is naturally recursive because trees have a recursive structure (each node has subtrees).",
        difficulty=3  # Medium-hard - pattern recognition
    )
]


# Queue & Priority Queue Quiz Questions
QUEUE_QUIZ = [
    QuizQuestion(
        question="What is the primary acronym used to describe Queue behavior?",
        options=[
            "LIFO (Last-In, First-Out)",
            "FIFO (First-In, First-Out)",
            "FILO (First-In, Last-Out)",
            "LILO (Last-In, Last-Out)"
        ],
        correct_index=1,
        explanation="Queues follow FIFO — First-In, First-Out. The first element added is always the first one removed, just like a line at a coffee shop.",
        difficulty=1  # Easy - basic concept
    ),

    QuizQuestion(
        question="In a Priority Queue, which element is always the first to be removed?",
        options=[
            "The element that was added first",
            "The element that was added last",
            "The element with the highest priority (lowest value by default)",
            "A randomly selected element"
        ],
        correct_index=2,
        explanation="A PriorityQueue always removes the highest-priority element first. By default in Java, this means the smallest numeric value (min-heap).",
        difficulty=1  # Easy - core distinction
    ),

    QuizQuestion(
        question="Unlike an ArrayList, which operation is strictly forbidden in a standard Queue?",
        options=[
            "Adding an element to the back",
            "Removing the front element",
            "Accessing an element by index",
            "Checking if the Queue is empty"
        ],
        correct_index=2,
        explanation="A Queue only allows interaction at the front and back. Random access by index (like get(2)) is not supported — that would break the FIFO contract.",
        difficulty=2  # Medium - structural constraint
    ),

    QuizQuestion(
        question="Where does offer() place a new element in a Queue?",
        options=[
            "At the front of the Queue",
            "At a random position",
            "At the back (rear) of the Queue",
            "In sorted order"
        ],
        correct_index=2,
        explanation="offer() always adds to the back of the Queue. Elements exit from the front — that's what makes it FIFO (First-In, First-Out).",
        difficulty=2  # Medium - structural understanding
    ),

    QuizQuestion(
        question="If you insert 50, 10, and 30 into a Java PriorityQueue (default ordering) and call poll(), which value is returned?",
        options=[
            "50 — it was inserted first",
            "30 — it is the middle value",
            "10 — it has the highest priority (smallest value)",
            "The result is unpredictable"
        ],
        correct_index=2,
        explanation="Java's default PriorityQueue is a min-heap — poll() always returns the smallest value regardless of insertion order. 10 exits first even though 50 was inserted first.",
        difficulty=3  # Hard - requires tracing PriorityQueue behavior
    )
]


# Use 5 questions for each topic
ARRAYLIST_QUIZ_FINAL = ARRAYLIST_QUIZ[:5]
RECURSION_QUIZ_FINAL = RECURSION_QUIZ[:5]
QUEUE_QUIZ_FINAL = QUEUE_QUIZ[:5]


def get_quiz(topic_key: str) -> List[QuizQuestion]:
    """Get the quiz for a specific topic."""
    if topic_key == 'arraylist':
        return ARRAYLIST_QUIZ_FINAL
    elif topic_key == 'recursion':
        return RECURSION_QUIZ_FINAL
    elif topic_key == 'queue':
        return QUEUE_QUIZ_FINAL
    else:
        return []


def score_quiz(topic_key: str, user_answers: dict) -> tuple:
    """
    Score a quiz.

    Args:
        topic_key: 'arraylist', 'recursion', or 'queue'
        user_answers: dict mapping question index to selected answer text

    Returns:
        (score, total, results_list)
        results_list contains dicts with question, user_answer, correct_answer, is_correct, difficulty
    """
    quiz = get_quiz(topic_key)
    results = []
    score = 0

    for i, question in enumerate(quiz):
        user_answer = user_answers.get(i)
        correct_answer = question.options[question.correct_index]
        is_correct = user_answer == correct_answer

        if is_correct:
            score += 1

        results.append({
            'question': question.question,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question.explanation,
            'difficulty': question.difficulty  # Include difficulty in results
        })

    return score, len(quiz), results
