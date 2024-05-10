from multiprocessing import Process

def background_task():
    print("This is a background task")
    # Your code here

process = Process(target=background_task)
process.start()
print("Main program continues to run in foreground.")
process.join()
