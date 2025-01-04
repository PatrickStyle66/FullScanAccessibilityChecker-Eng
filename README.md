# Full-Scan Accessibility Checker
A full-scan accessibility checker, that is, a checker capable of performing accessibility verification on all pages of a website. The tool consists of three main components: the web crawler, which searches for the pages of a website; the evaluator, which performs the accessibility verification of each page; and the user interface.

The web crawling process and the coordination of the analysis process are implemented using the Selenium tool, which provides a webdriver for accessing and interacting with websites, especially those with dynamic content. During the tool's operation, the webdriver uses three browser tabs with specific functions assigned to each: the first tab is responsible for accessing the website's homepage and searching for additional pages; the second tab accesses the Access Monitor checker and performs accessibility verification of pages; and finally, the third tab accesses the other pages found on the homepage and continues the process of searching for more pages.

For locating and interacting with elements on web pages, XPATH queries are used to select nodes in an HTML document through defined filters. These filters not only locate elements but also exclude undesirable links during the page search process, such as social media links or media elements like photos and videos. The latter do not need individual analysis because the checker can evaluate them within the page.

The interface is implemented simply using the Streamlit framework, which facilitates data visualization and interaction. During the page evaluation process, the information provided by the Access Monitor evaluation report is collected and stored in a dataframe to be later displayed in the user interface. Other information, such as images generated by the report, also forms part of the final display in the interface.
