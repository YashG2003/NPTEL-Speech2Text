import os
import time
import requests
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import shutil

class DataDownloader:
    def __init__(self, course_url: str):
        self.course_url = course_url

    def setup_selenium(self):
        """Setup the Selenium WebDriver for Chrome."""
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")              # Disable GPU acceleration
        chrome_options.add_argument("--window-size=1920x1080")    # Set window size
        chrome_options.add_argument("--headless=new")             # Add the headless argument
        # Debugging of code can be done by removing the headless arguement, we can see the simulation 

        # Configure Chrome to suppress "Show downloads when they're done" notification
        prefs = {
            "download.default_directory": os.path.abspath("downloads"),      # Default download directory
            "plugins.always_open_pdf_externally": True,                      # Bypass PDF viewer to directly download
            "download.prompt_for_download": False,                           # Disable download prompts
            "profile.default_content_setting_values.automatic_downloads": 1  # Suppress download notifications
        }
        chrome_options.add_experimental_option("prefs", prefs)

        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def download_transcripts(self, downloads_folder: str, transcripts_folder: str):
        """Download lecture transcripts (PDFs) from the course page."""
        driver = self.setup_selenium()
        driver.get(self.course_url)
        wait = WebDriverWait(driver, 30)

        try:
            # Open the "Download" pane
            print("Opening Download pane...")
            download_pane = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'tab') and contains(text(), 'downloads')]"))
            )
            download_pane.click()

            # Open "Transcripts" dropdown
            print("Opening Transcripts dropdown...")
            transcripts_dropdown = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'type')]/h3[text()='Transcripts']"))
            )
            transcripts_dropdown.click()

            # Locate all parent elements with "Select Language" and "Transcripts" button
            print("Locating parent elements with 'Select Language' and 'Transcripts' button...")
            parents = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'c-language')]"))
            )
            print(f"Found {len(parents)} parent elements to process.")

            # Create output directory if it doesn't exist
            os.makedirs(transcripts_folder, exist_ok=True)

            # Process each parent element
            for i, parent in enumerate(parents, start=1):
                print(f"Processing parent element {i}...")

                # Define the dropdown element
                dropdown = parent.find_element(By.XPATH, ".//div[contains(@class, 'pseudo-input')]")

                # Scroll to the dropdown and click it
                driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
                
                dropdown.click()
                
                time.sleep(3)

                # Select "English-Verified" option
                print("Selecting language: English-Verified...")
                english_verified_option = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//ul[@class='pseudo-options show']")
                    )
                )
                english_verified_option.click()

                # Find the sibling element containing the "Transcripts" button
                print("Finding sibling containing the 'Transcripts' button...")
                sibling = parent.find_element(
                    By.XPATH, ".//following-sibling::div[descendant::button[contains(text(), 'Transcripts')]]"
                )
                
                time.sleep(3)
                
                # Define the "Transcripts" button with href link
                button = sibling.find_element(
                    By.XPATH, ".//button[@class='download-btn' and not(@disabled)]"
                )

                # Wait for the button to be clickable and make sure it's not obstructed by other elements
                print(f"Waiting for the button to be clickable for transcript {i}...")
                wait.until(EC.element_to_be_clickable(button))
                driver.execute_script("arguments[0].scrollIntoView(true);", button)

                # Use JavaScript to click the button if normal clicking fails due to obstructions
                try:
                    print(f"Opening transcript {i} in a new tab...")
                    button.click()
                except Exception as e:
                    print(f"Normal click failed, using JavaScript click: {e}")
                    driver.execute_script("arguments[0].click();", button)

                time.sleep(3)

                # Switch to the new tab
                driver.switch_to.window(driver.window_handles[-1])

                # Interact with the download button in the Google Drive interface
                print("Clicking the download button...")
                download_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label, 'Download') and @role='button']"))
                )
                download_button.click()

                # Wait 15 seconds for the file to download and stabilize
                # this time of 15 seconds should be changed depending on size of files
                print(f"Waiting for transcript {i} to be downloaded...")
                time.sleep(15)  

                # Close the current tab and return to the main tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            print("All transcripts have been successfully downloaded.")

            # Move all downloaded files from the "downloads" folder to the "transcripts" folder
            print("Moving downloaded files to the transcripts folder...")
            for file in os.listdir(downloads_folder):
                if file.endswith(".pdf"):
                    src_path = os.path.join(downloads_folder, file)
                    dest_path = os.path.join(transcripts_folder, file)
                    shutil.move(src_path, dest_path)
                    print(f"Moved {file} to {transcripts_folder}")

            print("All files have been moved successfully.")

        except Exception as e:
            print(f"Error downloading transcripts: {e}")
        finally:
            driver.quit()


    def download_videos(self, output_dir: str):
        """Download lecture videos (MP4) using Selenium and ffmpeg."""
        driver = self.setup_selenium()
        driver.get(self.course_url)
        wait = WebDriverWait(driver, 20)

        try:
            # Click on the "Download" pane
            print("Opening Download pane...")
            download_pane = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'tab') and contains(text(), 'downloads')]"))
            )
            download_pane.click()
            time.sleep(2)

            # Open "Videos" dropdown
            print("Opening Videos dropdown...")
            videos_dropdown = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'type')]/h3[text()='Videos']"))
            )
            videos_dropdown.click()
            time.sleep(2)

            # Locate all download buttons
            print("Locating download buttons...")
            download_buttons = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class, 'type') and .//h3[text()='Videos']]//div[contains(@class, 'd-data')]//button[contains(@class, 'download-btn') and text()='Download']")
                )
            )
            print(f"Found {len(download_buttons)} videos.")

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            for i, button in enumerate(download_buttons, start=1):
                try:
                    print(f"Processing video {i}...")

                    # Scroll to the button and click it
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(2)
                    button.click()

                    # Switch to the new tab
                    time.sleep(3)
                    driver.switch_to.window(driver.window_handles[-1])

                    # Extract video URL from the new tab
                    print("Extracting video source URL...")
                    video_source = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//video/source[contains(@src, '.mp4')]"))
                    )
                    video_url = video_source.get_attribute("src")

                    if video_url:
                        print(f"Downloading video {i} from {video_url} using ffmpeg...")

                        # Define output file path
                        output_file = os.path.join(output_dir, f"video_{i}.mp4")

                        # Run ffmpeg command
                        command = [
                            "ffmpeg",
                            "-i", video_url,   # Input URL
                            "-c", "copy",      # Direct copy without re-encoding
                            output_file        # Output file path
                        ]
                        try:
                            subprocess.run(command, check=True)
                            print(f"Video {i} saved to {output_file}")
                        except subprocess.CalledProcessError as e:
                            print(f"Failed to download video {i}: {e}")
                    else:
                        print(f"Video {i} URL not found.")

                    # Close the current tab and switch back to the main tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    print(f"Error processing video {i}: {e}")

            print("All videos have been processed.")

        except Exception as e:
            print(f"Error downloading videos: {e}")

        finally:
            driver.quit()
        

    '''
    def download_videos(self, output_dir: str):
        """Download lecture videos (MP4) using Selenium and the requests library."""
        driver = self.setup_selenium()
        driver.get(self.course_url)
        wait = WebDriverWait(driver, 20)

        try:
            # Click on the "Download" pane
            print("Opening Download pane...")
            download_pane = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'tab') and contains(text(), 'downloads')]"))
            )
            download_pane.click()
            time.sleep(2)

            # Open "Videos" dropdown
            print("Opening Videos dropdown...")
            videos_dropdown = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'type')]/h3[text()='Videos']"))
            )
            videos_dropdown.click()
            time.sleep(2)

            # Locate all download buttons
            print("Locating download buttons...")
            download_buttons = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class, 'type') and .//h3[text()='Videos']]//div[contains(@class, 'd-data')]//button[contains(@class, 'download-btn') and text()='Download']")
                )
            )
            print(f"Found {len(download_buttons)} videos.")

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            for i, button in enumerate(download_buttons, start=1):
                try:
                    print(f"Processing video {i}...")

                    # Scroll to the button and click it
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(2)
                    button.click()

                    # Switch to the new tab
                    time.sleep(3)
                    driver.switch_to.window(driver.window_handles[-1])

                    # Extract video URL from the new tab
                    print("Extracting video source URL...")
                    video_source = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//video/source[contains(@src, '.mp4')]"))
                    )
                    video_url = video_source.get_attribute("src")

                    if video_url:
                        print(f"Downloading video {i} from {video_url} using requests...")

                        # Define output file path
                        output_file = os.path.join(output_dir, f"video_{i}.mp4")

                        # Download the video using requests
                        try:
                            response = requests.get(video_url, stream=True)
                            response.raise_for_status()  # Raise an error for bad status codes

                            # Write the video content to the file
                            with open(output_file, "wb") as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)

                            print(f"Video {i} saved to {output_file}")
                        except requests.RequestException as e:
                            print(f"Failed to download video {i}: {e}")
                    else:
                        print(f"Video {i} URL not found.")

                    # Close the current tab and switch back to the main tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    print(f"Error processing video {i}: {e}")

            print("All videos have been processed.")

        except Exception as e:
            print(f"Error downloading videos: {e}")

        finally:
            driver.quit()
    '''


if __name__ == "__main__":
    course_url = "https://nptel.ac.in/courses/106106184"  

    downloader = DataDownloader(course_url)

    downloads_path = "./downloads"           
    transcripts_path = "./transcripts_trial"      
    videos_path = "./videos"

    # Download transcripts
    downloader.download_transcripts(downloads_path, transcripts_path)

    # Download videos
    downloader.download_videos(videos_path)
    



