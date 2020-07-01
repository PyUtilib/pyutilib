import pyutilib.workflow
import tasks_yz

driver = pyutilib.workflow.TaskDriver()
driver.register_task('TaskZ')
driver.register_task('TaskY')

print(driver.parse_args())
