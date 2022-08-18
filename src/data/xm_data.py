from multiprocessing.connection import wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os

# source
## https://stackoverflow.com/questions/45653801/selenium-wait-for-element-to-be-clickable-not-working

## custom function for waiting to be clickable
def wait_for_element_to_be_clickable(browser, selector, timeout=10):
    wd_wait = WebDriverWait(browser, timeout)

    value = wd_wait.until(
        EC.element_to_be_clickable(selector),
        message="waiting for element to be clickable",
    )
    print("WAITING")
    return value


## custom function for clickable wait function that relies on exceptions. """
def custom_wait_clickable_and_click(
    driver, selector, item_name, attempts=5, t4wait=10, tout=10
):
    print("Trying to click: " + item_name)
    count = 0
    while count < attempts:
        try:
            time.sleep(t4wait)

            # This will throw an exception if it times out, which is what we want.
            # We only want to start trying to click it once we've confirmed that
            # selenium thinks it's visible and clickable.
            elem = wait_for_element_to_be_clickable(driver, selector, timeout=tout)
            elem.click()
            return elem

        except WebDriverException as e:
            if "is not clickable at point" in str(e):
                print("Retrying clicking on button.")
                count = count + 1
            else:
                raise e

    raise TimeoutException("custom_wait_clickable timed out" + item_name)


## function for checking if the file was donwloaded
### source
# https://stackoverflow.com/questions/34338897/python-selenium-find-out-when-a-download-has-completed
def download_wait(directory, timeout, nfiles=None):
    """
    Wait for downloads to finish with a specified timeout.
    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.
    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        print(files)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            if fname.endswith(".crdownload"):
                dl_wait = True

        seconds += 1
    return seconds


def dr_options(webdriver, dw_path, dr_path):
    """
    This fun sets the chrome driver options
    """
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": dw_path}
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1420,1080")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-notifications")
    ser = Service(dr_path)
    browser = webdriver.Chrome(service=ser, options=options)
    return browser


# start browsing
def click_call(flow: str, dw_path: str, tm_constant: int, args: dict):
    """
    This fun will click in the Procomer page to get the desire data
    The first parameter that we need to set is the flow, with that trigger we can get
    "x" exports or "m" imports. The second is the desired path and the time to wait.
    """
    # set the main page
    args["driver"].get("http://sistemas.procomer.go.cr/estadisticas/inicio.aspx")

    # select flow
    if flow == "x":
        custom_wait_clickable_and_click(
            selector=(By.ID, "ASPxTabControl1_AT0"), item_name="flow", **args
        )
    else:
        custom_wait_clickable_and_click(
            selector=(By.ID, "ASPxTabControl1_T1"), item_name="flow", **args
        )

    # apply manual 6
    custom_wait_clickable_and_click(
        selector=(By.ID, "ASPxRoundPanel2_RBValorST"), item_name="manual6", **args
    )

    # removing region
    custom_wait_clickable_and_click(
        selector=(By.ID, "ASPxRoundPanel2_CBRegion"), item_name="region", **args
    )

    # apply regimen
    custom_wait_clickable_and_click(
        selector=(By.ID, "ASPxRoundPanel2_CBRegimen"), item_name="chapter", **args
    )

    # years
    ## check years box
    custom_wait_clickable_and_click(
        selector=(By.ID, "ASPxPivotGrid1_sortedpgHeader0F"),
        item_name="checkbox_year",
        **args
    )
    ## select all years
    custom_wait_clickable_and_click(
        selector=(By.ID, "ASPxPivotGrid1FTRIAll"), item_name="all_years", **args
    )
    ## apply changes
    custom_wait_clickable_and_click(
        selector=(By.ID, "ASPxPivotGrid1_FPWOK_CD"), item_name="apply_years", **args
    )

    # download
    custom_wait_clickable_and_click(
        selector=(By.ID, "ASPxRoundPanel3_ImageButton3"),
        item_name="download_click",
        **args
    )

    ## check if file was downloaded
    download_wait(dw_path, tm_constant)

    # close
    args["driver"].close()
    args["driver"].quit()
