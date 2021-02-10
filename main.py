import asyncio
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

pod_list_command = "kubectl get pods | grep Running"
pod_command = "kubectl exec %s -- jcmd 1 Thread.print"
dumps_per_pod = 10
sleep_seconds = 5
create_zip = True

logLevel = logging.INFO
logging.basicConfig(stream=sys.stdout, level=logLevel)


def get_timestamp():
    dt = datetime.now()
    return dt.strftime("%d-%m-%Y-%H-%M-%S-%f")


timestamp = get_timestamp()
root_dir = "output/threaddumps-{0}".format(timestamp)
Path(root_dir).mkdir(parents=True)


async def write_threaddump(pod_id):
    proc = await asyncio.create_subprocess_shell(
        pod_command % pod_id,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    logging.debug("To file: %s" % pod_id)
    if stdout:
        with open("{0}/{1} - {2}.txt".format(root_dir, pod_id, get_timestamp()), "w") as file:
            file.write(stdout.decode())
    if stderr:
        logging.error("Pod %s error: %s" % (pod_id, stderr.decode()))


async def main():
    for i in range(0, dumps_per_pod):
        pods = os.popen(pod_list_command).readlines()
        tasks = []
        for pod in pods:
            pod_id = pod.split()[0]
            logging.debug("cycle: %s, pod %s" % (i, pod_id))
            task = asyncio.ensure_future(write_threaddump(pod_id))
            tasks.append(task)
        await asyncio.gather(*tasks)
        logging.info("All pods processed [{0}/{1}]".format(i+1, dumps_per_pod))
        time.sleep(sleep_seconds)

if __name__ == '__main__':
    asyncio.run(main())
    if create_zip:
        shutil.make_archive(root_dir, 'zip', root_dir)

