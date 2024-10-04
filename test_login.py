import inspect
import logging
import time
from enum import Enum
from functools import wraps

import pytest
from playwright.sync_api import expect, Playwright
from playwright.sync_api._generated import Locator, Page

logging.basicConfig(level=logging.INFO)


# decorator to calculate duration
# taken by any function.
def record_screen(func):
    # added arguments inside the inner1,
    # if function takes any arguments,
    # can be added like this.
    @wraps(func)
    def inner1(*args, **kwargs):
        # storing time before function execution
        begin = time.time()
        res = None
        try:
            print("in decorator")
            res = func(*args, **kwargs)
            print(inspect.stack()[1].function)
        except Exception as e:
            print("Error")
            return res
        # storing time after function execution
        end = time.time()
        print("Total time taken in : ", func.__name__, end - begin)

    return inner1


# Defining the text that will be used in the tests to avoid typos.
class Text(Enum):
    LOADING_YOUR_DAILY_TIP = "Loading your daily tip..."
    STAY_FOCUSED_AND_PRIORITIZE = (
        "Stay focused and prioritize your most important tasks!"
    )
    TASK_MANAGER = "Task Manager"
    DAILY_TIP = "Daily Tip"
    ADD_NEW_TASK = "Add New Task"
    TASK_LIST = "Task List"
    ADD_TASK = "Add Task"
    SET_PRIORITY = "Set Priority"
    COMPLETED_TASKS = "Completed Tasks"
    SHOW_COMPLETED_TASKS = "Show Completed Tasks"


def get_current_page(page):
    return page.locator("//body")


class BaseElement(Locator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self, "The element was not found."

    def _locator(self, xpath: str, *args, **kwargs):
        return self.locator(f"xpath={xpath}", *args, **kwargs)

    def locate(self, xpath: str, wait: int = 0, *args, **kwargs):
        time_start = time.time()
        found = False
        if not wait:
            return self._locator(xpath, *args, **kwargs)
        while not found and (time.time() - time_start < wait):
            if self._locator(xpath, *args, **kwargs):
                return self._locator(xpath, *args, **kwargs)
            time.sleep(0.1)  # To avoid CPU hogging
        else:
            raise TimeoutError(
                f"Element with xpath: {xpath}\n not found withing timeframe {wait}s "
            )


class Card(BaseElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # We'll be able to access all title elements with this property.
    @property
    def title(self):
        return self.get_attribute(".//h2")


class TaskManagerPage(BaseElement):
    def __init__(self, body: Locator):
        super().__init__(body)
        self.daily_tip_card_text = Text.DAILY_TIP.value
        self.add_new_task_card_text = Text.ADD_NEW_TASK.value
        self.task_list_card_text = Text.TASK_LIST.value
        self.completed_tasks_card_text = Text.COMPLETED_TASKS.value

        self.card_base_xpath = ".//div/*[contains(text(), '{text}')]/parent::div"

        self.daily_tip_card = TaskManagerPage.DailyTipCard(
            self.locate(self.card_base_xpath.format(text=self.daily_tip_card_text))
        )
        self.add_new_task_car = TaskManagerPage.AddNewTaskCard(
            self.locate(self.card_base_xpath.format(text=self.add_new_task_card_text))
        )
        self.task_list_card = TaskManagerPage.TaskListCard(
            self.locate(self.card_base_xpath.format(text=self.task_list_card_text))
        )
        self.completed_tasks_card = TaskManagerPage.CompletedTasks(
            self.locate(
                self.card_base_xpath.format(text=self.completed_tasks_card_text)
            )
        )

    class DailyTipCard(Card):
        def __init__(self, body: Locator):
            super().__init__(body)
            self.tip_text_xpath = ".//p"

        # We do not want to initialize the tip_text_elem until we need it.
        @property
        def tip_text_elem(self):
            return self.locate(self.tip_text_xpath)

    class AddNewTaskCard(Card):
        def __init__(self, body: Locator):
            super().__init__(body)
            self.input_field_xpath = ".//input"
            self.button_xpath = ".//button"
            self.button = self.locate(self.button_xpath)
            self.input_field = self.locate(self.input_field_xpath)

    class TaskListCard(Card):
        def __init__(self, body: Locator):
            super().__init__(body)
            self.task_list_xpath = ".//ul"
            self.task_list = None

        def init_task_list(self) -> BaseElement:
            self.task_list = self.locate(self.task_list_xpath)
            return self.task_list

        @property
        def is_task_list_initialized(self):
            return self.task_list

        class TaskList(BaseElement):
            def __init__(self, body: Locator):
                super().__init__(body)
                self.task_xpath = ".//li"
                self.tasks = self.populate_tasks()

            def populate_tasks(self):
                self.tasks = self.locate(self.task_xpath)
                return self.tasks

            @property
            def is_populated(self):
                return bool(self.tasks)

            class TaskWithCheckbox(BaseElement):
                def __init__(self, body: Locator):
                    super().__init__(body)
                    self.task_text_xpath = ".//span"
                    self.checkbox_xpath = ".//input"
                    self.button_xpath = ".//button"

                    self.checkbox = self.locate(self.checkbox_xpath)
                    self.button = self.locate(self.button_xpath)

                @property
                def text(self):
                    return self.locate(self.task_text_xpath).inner_text()

                @property
                def is_text_line_through(self):
                    style = self.locate(self.task_text_xpath).get_attribute("style")
                    return "line-through" in style

                class Checkbox(BaseElement):
                    def __init__(self, body: Locator):
                        super().__init__(body)

    class CompletedTasks(Card):
        def __init__(self, body: Locator):
            super().__init__(body)


class TestTaskManager:
    @pytest.fixture(scope="function", autouse=True)
    def before_each_after_each(self, page: Page):
        print("before the test runs")
        # Go to the starting url before each test.
        # browser = playwright.chromium.launch()
        # context = browser.new_context(record_video_dir="./videos/")
        # page = context.new_page()
        page.goto("https://demo.visionect.com/tasks/index.html")
        assert page, "The page did not load correctly."
        self.task_manager_page = TaskManagerPage(get_current_page(page))
        yield

        print("after the test runs")

    # @record_screen
    def test_01_task_manager_text(self, request):
        time_start = time.time()
        found = False
        expect(self.task_manager_page.daily_tip_card.tip_text_elem).to_have_text(
            Text.STAY_FOCUSED_AND_PRIORITIZE.value, timeout=1000
        )
