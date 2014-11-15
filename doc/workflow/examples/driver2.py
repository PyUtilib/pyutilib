import pyutilib.workflow
import tasks_yz

driver = pyutilib.workflow.TaskDriver(prog='myprog',
   description='This is the description of this task driver',
   epilog="""**********************
This is more text
that describes this command driver.  Note

that the format of the epilog string is preserved in the
help
output!
**********************
""")
driver.register_task('TaskZ')
driver.register_task('TaskY')

print(driver.parse_args())
