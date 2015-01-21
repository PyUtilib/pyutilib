import pyutilib.workflow
import pyutilib.component.core

# @usage:
import tasks_yz

driver = pyutilib.workflow.TaskDriver()
driver.register_task('TaskZ')
driver.register_task('TaskY')

print(driver.parse_args(['TaskZ','--x=3','--y=4']))
print(driver.parse_args(['TaskY','--X=3','--Y=4']))
# @:usage
