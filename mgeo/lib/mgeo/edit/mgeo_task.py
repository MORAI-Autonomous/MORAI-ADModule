class MGeoTask:
    job_desc = 'append an object to a list'
    
    def __init__(self):
        # state 
        # 0: 작업 수행 전 
        # 1: 작업 수행 후 (undo 가능)
        # 2: undo 이후    (redo 가능)
        self.state = 0

    def do(self, list_obj, new_obj):
        # undo하기 위해 저장
        self.new_obj = new_obj
        self.list_obj = list_obj

        # 작업 수행
        self.list_obj.append(self.new_obj)
    
    def undo(self):
        self.list_obj.pop(-1)

    def redo(self):    
        # 작업 수행
        self.list_obj.append(self.new_obj)

    def to_string(self):
        print('{} (arg = {})'.format(job_desc, self.new_obj))