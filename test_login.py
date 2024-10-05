import inspect
import logging
import time
from enum import Enum
from functools import wraps

import pytest
from playwright.sync_api import expect, Playwright
from playwright.sync_api._generated import Locator, Page

logging.basicConfig(level=logging.INFO)


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


class BaseElement:
    def __init__(self, locator: Locator):
        self.locator = locator
        assert self.locator, "The element was not found."

    def _locator(self, xpath: str, *args, **kwargs):
        return self.locator.locator(f"xpath={xpath}", *args, **kwargs)

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
        self.add_new_task_card = TaskManagerPage.AddNewTaskCard(
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
            self.task_list_xpath: str = ".//ul"
            self.task_list = ...

        def init_task_list(self) -> BaseElement:
            self.task_list = TaskManagerPage.TaskListCard.TaskList(
                self.locate(self.task_list_xpath)
            )
            return self.task_list

        @property
        def is_task_list_initialized(self):
            return bool(self.task_list)

        class TaskList(BaseElement):
            def __init__(self, body: Locator):
                super().__init__(body)
                self.task_xpath: str = ".//li"
                self.tasks: list[BaseElement] = []

            def initialize_tasks(self):
                tasks: list[Locator] = self.locate(self.task_xpath).all()
                for task in tasks:
                    self.tasks.append(
                        TaskManagerPage.TaskListCard.TaskList.TaskWithCheckbox(task)
                    )
                return self.tasks

            @property
            def is_populated(self):
                return bool(self.tasks)

            class TaskWithCheckbox(BaseElement):
                def __init__(self, body: Locator):
                    super().__init__(body)
                    self.task_text_xpath: str = ".//span"
                    self.checkbox_xpath: str = ".//input"
                    self.button_xpath: str = ".//button"

                    self.checkbox: BaseElement = (
                        TaskManagerPage.TaskListCard.TaskList.TaskWithCheckbox.Checkbox(
                            self.locate(self.checkbox_xpath)
                        )
                    )
                    self.button: BaseElement = self.locate(self.button_xpath)

                @property
                def text(self):
                    return self.locate(self.task_text_xpath).inner_text()

                @property
                def text_elem(self):
                    return self.locate(self.task_text_xpath)

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
        page.goto("https://demo.visionect.com/tasks/index.html")
        assert page, "The page did not load correctly."
        self.task_manager_page = TaskManagerPage(get_current_page(page))
        yield
        print("after the test runs")

    @pytest.mark.parametrize("tip_timeout", [1000, 2000, 3000, 4000])
    def test_01_task_manager_text(self, tip_timeout: int):
        expect(self.task_manager_page.daily_tip_card.tip_text_elem).to_have_text(
            Text.STAY_FOCUSED_AND_PRIORITIZE.value, timeout=tip_timeout
        ), (
            f"The daily tip text {Text.STAY_FOCUSED_AND_PRIORITIZE.value} "
            f"did not load within {tip_timeout}ms."
        )

    @pytest.mark.parametrize(
        "text",
        [
            "New Test Task!",
            "1234567890,",
            "!@#$%^&*()",
            "",
            " ",
            "abcdefghijklmnopqrstuvwxyz",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()",
        ],
    )
    def test_02_add_new_task(self, text):
        add_task_card = self.task_manager_page.add_new_task_card
        task_list_card = self.task_manager_page.task_list_card

        add_task_card.input_field.fill("New Test Task!")
        add_task_card.button.click()
        task_list_card.init_task_list()
        task_list_card.task_list.initialize_tasks()
        print(task_list_card.task_list.tasks[0].text)
        # time.sleep(1)
        expect(task_list_card.task_list.tasks[0].text_elem).to_have_text(text)
