import logging
import time
from enum import Enum

import pytest
from playwright.sync_api import expect, Page
from playwright.sync_api._generated import Locator

logging.basicConfig(level=logging.INFO)


def get_current_page(page):
    return page.locator("//body")


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


class BaseElement:
    def __init__(self, locator: Locator):
        self.locator = locator
        assert self.locator, "The element was not found."

    def __call__(self):
        return self.locator

    def _locator(self, xpath: str, *args, **kwargs):
        return self.locator.locator(f"xpath={xpath}", *args, **kwargs)

    def locate(self, xpath: str, wait: int = 0, *args, **kwargs):
        target_locator = self._locator(xpath, *args, **kwargs)
        if wait:
            try:
                target_locator.wait_for(state="attached", timeout=wait * 1000)
            except Exception:
                raise TimeoutError(
                    f"Element with xpath: {xpath}\n not found within timeframe {wait}s"
                )
        return target_locator


class TaskWithCheckboxAndButton(BaseElement):
    def __init__(self, locator: Locator):
        super().__init__(locator)
        self.task_text_xpath: str = ".//span"
        self.checkbox_xpath: str = ".//input"
        self.button_xpath: str = ".//button"

    @property
    def text_elem(self):
        return self.locate(self.task_text_xpath)

    @property
    def text(self):
        return self.text_elem.inner_text()

    @property
    def checkbox(self):
        return self.locate(self.checkbox_xpath)

    @property
    def button(self):
        return self.locate(self.button_xpath)

    @property
    def is_text_line_through(self):
        style = self.text_elem.get_attribute("style")
        return "line-through" in style


class TaskWithTextOnly(BaseElement):
    def __init__(self, locator: Locator):
        super().__init__(locator)

    @property
    def text(self):
        return self.locator.inner_text()


class Card(BaseElement):
    def __init__(self, locator: Locator):
        super().__init__(locator)

    # We'll be able to access all title elements with this property.
    @property
    def title(self):
        return self.locate(".//h2").inner_text()


class TaskManagerPage(BaseElement):
    def __init__(self, locator: Locator):
        super().__init__(locator)
        self.card_base_xpath = ".//div/*[contains(text(), '{text}')]/parent::div"

        self.daily_tip_card = TaskManagerPage.DailyTipCard(
            self.locate(self.card_base_xpath.format(text=Text.DAILY_TIP.value))
        )
        self.add_new_task_card = TaskManagerPage.AddNewTaskCard(
            self.locate(self.card_base_xpath.format(text=Text.ADD_NEW_TASK.value))
        )
        self.task_list_card = TaskManagerPage.TaskListCard(
            self.locate(self.card_base_xpath.format(text=Text.TASK_LIST.value))
        )
        self.completed_tasks_card = TaskManagerPage.CompletedTasks(
            self.locate(self.card_base_xpath.format(text=Text.COMPLETED_TASKS.value))
        )

    class DailyTipCard(Card):
        def __init__(self, locator: Locator):
            super().__init__(locator)
            self.tip_text_xpath = ".//p"

        # We do not want to initialize the tip_text_elem until we need it.
        @property
        def tip_text_elem(self):
            return self.locate(self.tip_text_xpath)

    class AddNewTaskCard(Card):
        def __init__(self, locator: Locator):
            super().__init__(locator)
            self.input_field_xpath = ".//input"
            self.button_xpath = ".//button"
            self.button = self.locate(self.button_xpath)
            self.input_field = self.locate(self.input_field_xpath)

    class TaskListCard(Card):
        def __init__(self, locator: Locator):
            super().__init__(locator)
            self.tasks_xpath: str = ".//li"
            self.tasks = []

        def init_tasks(self) -> list:
            task_list = self.locate(self.tasks_xpath).all()
            for task in task_list:
                self.tasks.append(TaskWithCheckboxAndButton(task))
            return self.tasks

        @property
        def are_tasks_present(self):
            return bool(self.tasks)

    class CompletedTasks(Card):
        def __init__(self, locator: Locator):
            super().__init__(locator)
            self.tasks_xpath: str = ".//li"
            self.show_completed_tasks_button_xpath = ".//button"
            self.tasks = []
            self.show_completed_tasks_button = self.locate(
                self.show_completed_tasks_button_xpath
            )

        def init_tasks(self) -> list:
            task_list = self.locate(self.tasks_xpath).all()
            for task in task_list:
                self.tasks.append(TaskWithTextOnly(task))
            return self.tasks

        @property
        def are_tasks_present(self):
            return bool(self.tasks)


class TestTaskManager:
    @pytest.fixture(scope="function", autouse=True)
    def before_each_after_each(self, page: Page):
        print("before the test runs")
        page.goto("https://demo.visionect.com/tasks/index.html")
        assert page, "The page did not load correctly."
        self.task_manager_page = TaskManagerPage(get_current_page(page))
        yield
        print("after the test runs")

    @pytest.mark.task_manager_text
    @pytest.mark.parametrize(
        "tip_timeout", [1000, 4000], ids=lambda t: f"timeout_{t}ms"
    )
    def test_01_task_manager_text(self, tip_timeout: int):
        expect(self.task_manager_page.daily_tip_card.tip_text_elem).to_have_text(
            Text.STAY_FOCUSED_AND_PRIORITIZE.value, timeout=tip_timeout
        ), (
            f"The daily tip text '{Text.STAY_FOCUSED_AND_PRIORITIZE.value}' "
            f"did not load within {tip_timeout}ms."
        )

    @pytest.mark.add_new_task
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
        ids=lambda t: f"task_{t[:10].strip()}",
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
