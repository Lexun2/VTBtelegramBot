from datetime import datetime,timedelta
import pygsheets
from pygsheets.client import Client

class GoogleTable:
    def __init__(self, credense_service_file: str="", googlesheet_file_url: str="") -> None:
        self.credense_service_file=credense_service_file
        self.googlesheet_file_url=googlesheet_file_url

    def _get_googlesheet_by_url(
            self, googlesheet_client: pygsheets.client.Client) -> pygsheets.Spreadsheet:
        """Get Google.Docs Table sheet by document url"""
        sheets: pygsheets.Spreadsheet = googlesheet_client.open_by_url(
            self.googlesheet_file_url
        )
        return sheets.sheet1

    def _get_googlesheet_client(self) -> Client:
        """It is authorized using the service key and returns the Google Docs client object"""
        return pygsheets.authorize(
            service_file=self.credense_service_file
        )

    def search_task_by_time(self,
                            date: str ="",
                            time: str="",
                            search_col1: int = 2,
                            search_col2: int = 3,
                            executor_col: int = 4,
                            task_col: int = 5,
                            deadline_time_col: int = 6,
                            task_send_col: int = 7,
                            reminder_col: int = 9,
                            ):
        """Поиск задачи и пересыл его в чат, если настало нужное время"""

        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client)
        res = []
        try:
            find_cell = wks.find(date, matchEntireCell=True, cols=(search_col1, search_col1))
            for cell in find_cell:
                try:
                    future_hours=(datetime.now() + timedelta(hours=1)).strftime('%H:%M') # +1 hour to now hour
                    find_cell_tasks_reminder = wks.find(future_hours, matchEntireCell=False, cols=(deadline_time_col, deadline_time_col), rows=(cell.row, cell.row))

                    for task in find_cell_tasks_reminder:
                        find_cell_row = task.row
                        task_send = wks.get_value((find_cell_row, task_send_col))
                        reminder = wks.get_value((find_cell_row, reminder_col))
                        if task_send == "Да" and reminder != "Да":
                            find_cell_row = task.row
                            task_col_res = wks.get_value((find_cell_row, task_col))
                            executor_col_res = wks.get_value((find_cell_row, executor_col))
                            deadline_time_col_res = wks.get_value((find_cell_row, deadline_time_col))
                            res.append(list((task_col_res, executor_col_res, deadline_time_col_res, 2)))
                            wks.update_value((find_cell_row, reminder_col), "Да")


                except Exception as e:
                    print('continue, Exception=',e)

                try:
                    find_cell2 = wks.find(time, matchEntireCell=True, cols=(search_col2, search_col2), rows=(cell.row, cell.row))
                    for task in find_cell2:
                        find_cell_row = task.row
                        task_send = wks.get_value((find_cell_row, task_send_col))
                        reminder = wks.get_value((find_cell_row, reminder_col))
                        if task_send != "Да":
                            task_col_res = wks.get_value((find_cell_row, task_col))
                            executor_col_res = wks.get_value((find_cell_row, executor_col))
                            deadline_time_col_res = wks.get_value((find_cell_row, deadline_time_col))
                            res.append(list((task_col_res, executor_col_res, deadline_time_col_res, 1)))
                            wks.update_value((find_cell_row, task_send_col),"Да")

                except Exception as e:
                    print('continue, Exception=',e)
                    continue
            return res if len(res) else -1
        except:
            return -1
