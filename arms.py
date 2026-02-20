from playwright.sync_api import sync_playwright
import time
import requests

LOGIN_URL = "https://arms.sse.saveetha.com"
ATTEND_URL = "https://arms.sse.saveetha.com/StudentPortal/AttendanceReport.aspx"
MYCOURSE_URL = "https://arms.sse.saveetha.com/StudentPortal/MyCourse.aspx"

USERNAME = "192524041"
PASSWORD = "edrin¹⁶⁷²⁰⁰⁸"

BOT_TOKEN = "8222719407:AAGnjdhdiUxaEmOABtnTlk8FjoGXdmzOFLY"
CHAT_ID = "8162954190"

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

print("Choose option")
print("1 → Monitor Attendance")
print("2 → Monitor Completed Courses")

choice = input("Enter 1 or 2: ").strip()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    page = browser.new_page()

    # LOGIN
    page.goto(LOGIN_URL)
    page.fill('input[type="text"]', USERNAME)
    page.fill('input[type="password"]', PASSWORD)
    page.get_by_text("LOGIN").click()
    page.wait_for_load_state("networkidle")

    # -------- ATTENDANCE --------
    if choice == "1":
        page.goto(ATTEND_URL)
        page.wait_for_selector("table")

        attendance_map = {}

        rows = page.locator("table tbody tr").all()
        for row in rows:
            cols = row.locator("td").all()
            if len(cols) >= 8:
                course = cols[2].inner_text().strip()
                percent = cols[7].inner_text().strip()
                attendance_map[course] = percent

        send_msg("Attendance monitoring started")

        while True:
            timestamp = time.strftime("%H:%M:%S")
            print("Checking attendance at", timestamp)
            send_msg(f"Checking attendance at {timestamp}")

            page.reload()
            page.wait_for_timeout(2000)

            rows = page.locator("table tbody tr").all()
            for row in rows:
                cols = row.locator("td").all()
                if len(cols) >= 8:
                    course = cols[2].inner_text().strip()
                    percent = cols[7].inner_text().strip()

                    if attendance_map.get(course) != percent:
                        send_msg(
                            f"{course} attendance changed "
                            f"{attendance_map.get(course)} → {percent}"
                        )
                        attendance_map[course] = percent

            time.sleep(30)

    # -------- COMPLETED COURSES --------
    elif choice == "2":
        page.goto(MYCOURSE_URL)
        page.wait_for_selector("text=COMPLETED COURSES")

        section = page.locator("text=COMPLETED COURSES").locator("xpath=ancestor::div[1]")
        table = section.locator("table")

        previous_count = table.locator("tbody tr").count()
        send_msg(f"Completed monitoring started. Current: {previous_count}")

        while True:
            timestamp = time.strftime("%H:%M:%S")
            print("Checking completed courses at", timestamp)
            send_msg(f"Checking completed courses at {timestamp}")

            page.reload()
            page.wait_for_timeout(2000)

            current_count = table.locator("tbody tr").count()

            if current_count != previous_count:
                send_msg(f"Completed courses changed {previous_count} → {current_count}")
                previous_count = current_count

            time.sleep(30)

    else:
        print("Invalid option")

    browser.close()
# git add .
# git commit -m "describe what you changed"
# git push
#BOT_TOKEN = "8222719407:AAGnjdhdiUxaEmOABtnTlk8FjoGXdmzOFLY"