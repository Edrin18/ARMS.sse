from playwright.sync_api import sync_playwright
import time
import winsound
from win10toast import ToastNotifier

LOGIN_URL = "https://arms.sse.saveetha.com"
ENROLL_URL = "https://arms.sse.saveetha.com/StudentPortal/Enrollment.aspx"
MYCOURSE_URL = "https://arms.sse.saveetha.com/StudentPortal/MyCourse.aspx"

USERNAME = "192524041"
PASSWORD = "edrin¹⁶⁷²⁰⁰⁸"

TARGET_CODE = "UBA0435"
TARGET_SLOT = "Slot A"

toaster = ToastNotifier()

print("Choose option")
print("1 → Monitor course in slot")
print("2 → Monitor completed course count")

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

    # -------- OPTION 1 --------
    if choice == "1":
        page.goto(ENROLL_URL)
        page.wait_for_selector("select")
        dropdown = page.locator("select").first

        print("Monitoring slot availability...")

        while True:
            dropdown.select_option(label=TARGET_SLOT)
            page.wait_for_timeout(2500)

            body_text = page.locator("body").inner_text()

            if TARGET_CODE in body_text:
                print("FOUND", time.strftime("%H:%M:%S"))
                winsound.Beep(1200, 600)
                toaster.show_toast(
                    "Course Found",
                    f"{TARGET_CODE} available in {TARGET_SLOT}",
                    duration=5,
                    threaded=True
                )
            else:
                print("Not found", time.strftime("%H:%M:%S"))

            time.sleep(30)

    # -------- OPTION 2 --------
    elif choice == "2":
        page.goto(MYCOURSE_URL)
        page.wait_for_selector("text=COMPLETED COURSES")

        def get_completed_count():
            # find the completed courses table
            section = page.locator("text=COMPLETED COURSES").locator("xpath=ancestor::div[1]")
            table = section.locator("table")
            rows = table.locator("tbody tr")
            return rows.count()

        previous_count = get_completed_count()
        print("Initial completed courses:", previous_count)

        print("Monitoring completed courses...")

        while True:
            page.reload()
            page.wait_for_timeout(2000)

            current_count = get_completed_count()

            if current_count > previous_count:
                print("Completed courses increased:", current_count)
                winsound.Beep(1500, 800)
                toaster.show_toast(
                    "Completed Courses Updated",
                    f"Now completed: {current_count}",
                    duration=5,
                    threaded=True
                )
                previous_count = current_count
            else:
                print("No change", time.strftime("%H:%M:%S"))

            time.sleep(30)

    else:
        print("Invalid option")

    input("Press ENTER to close")
    browser.close()
