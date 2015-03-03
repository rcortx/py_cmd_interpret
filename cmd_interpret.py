#!/usr/bin/python
# cmd_interpret.py by Cubohan
# circa 2016

"""
<h2>'Plug and Play' Command line arguments parser and compiler</h2>
        
<h4>Best used to test various functions with different parameters 
          (EG: For parametric tuning) passed from the commandline in real time. 
          Supports automatic range based parameter testing.</h4>

### CONSTRUCTOR PARAMETERS
        
    (Check in-line documentation)

#### **PROPERTIES**
        
        **knobs**
        **flags**
        **msg**
        **exit_str**

#### **METHODS**
        
        (Check in-line documentation)

        **input()**

        **is_set(flag)**

        **get_options()**

        **exit()**

        **iterate_options()**

        **beep()**

        **log()**

        **log_time(t0, [msg])**

        **execute([n, log])**

"""

from types import GeneratorType
import winsound
from time import time

class CMD_IN(object):
    # CONSTANTS
    RANGE_DELIMITER = ':' # Delimiter for range queries from cmd paramters; 
    # Format: BEGIN:END:STEP
    
    DEFAULT_EXIT_STR = "xx" # User input to request exit from utility

    MSG_INDEXED_KNOB_FOUND = "KNOB referrence by index found! :: {}"
    MSG_OPTIONS_COMPILED = "Options Compiled :: {}"
    MSG_FLAGS_STATUS = "Flags status :: {}"
    
    MSG_LOG_TIME = "Time taken {}:\n{}"

    # Error messages
    MSG_ERROR_LOG = "Can't be logged: @ "
    MSG_ERROR_EXEC = "No executable setting found!"

    # Input prompt information
    MSG_PARAMETER_GUIDE = "Parameters: (May also use zero based index to set)"
    MSG_FLAG_GUIDE = "Flags:"
    MSG_EXIT_GUIDE = "EXIT: type {}"
    MSG_INPUT_PROMPT = "Enter Input? Options:{}__"
    
    # Reset annotations
    MSG_RESET_FLAGS = "Reseting All flags..."
    MSG_RESET_OPTIONS = "Reseting All Options..."

    MSG_EXECUTION = "Executing with options: {}"
    MSG_RESULT = "Result : {}"

    FREQ = 1000 # Set Frequency To 2500 Hertz
    DUR = 300 # Set Duration To 1000 ms == 1 second

    @property
    def knobs(self):
        return self._knobs
    
    @knobs.setter
    def knobs(self, kno): # 'kno' may be a tuple of (knobs, parsers) to change parsers with knobs well
        if type(kno[0]) == list or type(kno[0]) == tuple: 
            kno, self.parsers = kno 
        self._knobs = {k:(self.parsers[ind] if ind<len(self.parsers) 
            else float) for ind, k in enumerate(kno)}

    @property
    def flags(self):
        return self._flags
    
    @flags.setter
    def flags(self, f):
        self._flags = {a:False for a in f}
    
    @property
    def msg(self):
        return self._msg

    @msg.setter
    def msg(self, m):
        self._msg = m.format(self._pack(self.MSG_PARAMETER_GUIDE
            ) + str(self.knobs.keys())+ self._pack(self.MSG_FLAG_GUIDE) +str(self.flags)+
        self._pack(self.MSG_EXIT_GUIDE).format(self.exit_str)) if m else self._pack(
        self.MSG_INPUT_PROMPT)
    
    @property
    def exit_str(self):
        return self._exit_str
    
    @exit_str.setter
    def exit_str(self, k):    
        self._exit_str = k if k else self.DEFAULT_EXIT_STR
    
    def __init__(self, knobs, msg="", flags=[], 
        parsers=[], resetopts=False, includeflags=False, verbose=False, 
        resetflags=True, exit_str=None, logger=None, executable=None, enable_beep=False,
        permute_ranges=False):
        """
        #### **(REQUIRED)**
        @param: knobs: List -List of all parameters with (range of values) to be accepted. 
                        -These are only accepted as pairs from cmd in format: 
                         KNOB_NAME KNOB_VALUE
                        -KNOB_NAME may be replaced with index of the same in this list 
                         from cmd
                
        #### **(OPTIONALS)**
        @param: msg: string -Msg to display each time USER is promted for input. 
                      -MUST HAVE ONE PAIR of CURLY BRACES {} in string which is used to 
                       display available options automatically
                
        @param: flags: List -List of all flags. FORMAT: FLAG_NAME
                        -Will Toggle FLAG_NAME or if 'resetflags' is TRUE, will ENABLE FLAG_NAME 
                
        @param: parsers: List -List of functions to be called to parse corresponding (by index) 
                           KNOB_VALUE obtained
                          -Default parsing fucntion is float
                          -Co-relates with knobs by index in array
                          -If passed, can be filled partially (i.e providing parsing functions 
                           for first N KNOBS only. For the rest, float will be automatically used)
                
        @param: resetops: Bool -Set to TRUE to reset KNOB options before input is promted every time
                           -Default is FALSE. i.e KNOW_VALUES are carried over from previous inputs 
                            if not provided in this iteration in cmd
                
        @param: includeflags: Bool -Set to True to include flags in compiled options DICT output for further 
                                usage
                               -Default is False, i.e. falgs not included in compiled options DICT        

        @param: resetflags: Bool -Set to False to disable reseting Flag values on each iteration, i.e. 
                              carrying over previous flag values to current interation
                             -Default is TRUE

        @param: verbose: Bool -Set to True to enable operational commentary 

        @param: exit_str: string -String used to signal exit by user through input
                           -DEFAULT 'xx'
        
        @param: logger: Out-stream Obj -logging output stream object
        
        @param: executable: function -function to be called with selected options passed as arguments
        
        @param: enable_beep: Bool -set to enable beeping sound after completing execution
        
        @param: permute_ranges: Bool -set to partially permute options for ranged input
        """
        self.properties = {}
        self.parsers = parsers
        self.knobs = knobs
        self.knobs_indexed = knobs
        self.flags = flags
        self.exit_str = exit_str
        self.msg = msg

        self.opts = {}
        self.verbose = verbose
        self.includeflags = includeflags
        self.resetflags = resetflags
        self.resetopts = resetopts
        self.logger = logger
        self.executable = executable
        self.enable_beep = enable_beep
        self.permute_ranges = permute_ranges

        self._exit_flag = False
        self._generators = {}
        self._generators_to_permute = []
        self._range_is_active = False
    
    def input(self): # Ask user for input
        """
        Initiates user input from cmd
        """
        self._reset()
        inp = raw_input(self.msg).split()
        skip_next = False
        for ind, i in enumerate(inp):
            if skip_next:
                skip_next = False
                continue
            if i in self.flags:
                self.flags[i] = (not self.flags[i])
            elif i in self.knobs:
                self.opts[i] = self._parse(inp[ind+1], i)
                skip_next = True
            elif i == self.exit_str:
                self._exit_flag = True
            elif i.isdigit():
                key = self.knobs_indexed[int(i)]
                self._verbal(self._pack(self.MSG_INDEXED_KNOB_FOUND).format(key))
                self.opts[key] = self._parse(inp[ind+1], key)
                skip_next = True
        self._verbal(self._pack(self.MSG_OPTIONS_COMPILED) + self._pack(self.MSG_FLAGS_STATUS
            ).format(self.opts, self.flags))

    def get_options(self): # PRO-TIP: The returned dictionary can be **kwargs of any function
        """
        Return a dictionary of compiled options with parsed values
        """
        if self.includeflags:
            opts = {f:v for f, v in self.flags.items()}
            opts.update(self.opts)
            return self._yield(opts)
        return self._yield(self.opts)
    
    def iterate_options(self): # iterate over all permutaions of options automatically
        """
        Generator function to continuously generate options
        """
        opts = self.get_options()
        while opts:
            yield opts
            opts = self.get_options()

    def is_set(self, flag): # Check if flag is set to True
        """
        Check if 'flag' is set to True

        @param: flag: string key (REQUIRED)
        """
        return self.flags[flag]
    
    def exit(self): # Check if user has asked to exit
        """
        Check if user has prompted for EXIT. Flag (self.exit_str) is checked for 
        in provided input 
        """
        return self._exit_flag
    
    def beep(self): # PRO-TIP: use to indicate compeltion of execution of one iteration
        """
        Used to generate a beeping sound.
        """
        if self.enable_beep:
            winsound.Beep(self.FREQ,self.DUR)  
    def log(self, msg):
        """
        Log msg in provided logger
        @param: msg: string, message to be logged
        """
        if self.logger:
            self.logger.write(self._pack(msg))
        else: self._raise(self.MSG_ERROR_LOG + msg)
    
    def log_time(self, t0, msg=None):
        """
        Log time difference between t0 and now
        @param: t0: time object, time to be compared from now
        @param: masg: string, additional message to be logged to tag time diff
        """
        self.log(self.MSG_LOG_TIME.format("for " + msg if msg else "", time()-t0))
    
    def execute(self, n=0, log=True):
        """
        Execute functions with user given parameters
        @param: n: Integer, denotes number of iterations of executions. Defaults to 
                    1 iteration when not provided
        @param: log: Bool, indicates if logging (Included tiem taken) has to be 
                    performed post every iteration
        #param: beep: Bool, indicates if user has to prompted after task completion
        
        @return: results, results of all executions
        """
        if self.executable:
            results = []
            if (not n) and (not self._range_is_active): n = 1
            if n:
                iterator = self.iterate_options()
                for _ in range(n):
                    opts = iterator.next()
                    results.append(self._execute(self.executable, opts, log))   
            else: 
                results = [self._execute(self.executable, opts, log) for opts in self.iterate_options()]
            
            self.beep() # prompt the user about completion with beeping sound

            if len(results) == 1: 
                return results[0]
            return results
        else: self._raise(self.MSG_ERROR_EXEC)
    
    def _execute(self, func, opts, log):
        if log: t0 = time()
        res = func(**opts) 
        if log: 
            self.log_time(t0, msg=self.MSG_EXECUTION.format(opts)) 
            self.log(self.MSG_RESULT.format(res))
        return res
    
    def _reset(self): # rests flags internally
        if self.resetflags:
            self._verbal(self.MSG_RESET_FLAGS)
            for f in self.flags:
                self.flags[f] = False
        if self.resetopts:
            self._verbal(self.MSG_RESET_OPTIONS)
            self.opts = {}
        self._generators = {}
        self._generators_to_permute = []
    
    def _verbal(self, m):
        if self.verbose:
            print self._pack(m)
    
    def _pack(self, m):
        return "\n\n" + m + "\n\n"
    
    def _parse(self, val, key): # RANGE sytax BEGIN-END:STEP
        try:
            ind = val.index(self.RANGE_DELIMITER)
        except ValueError as e:
            ind = 0
        try:
            step_i = val.index(self.RANGE_DELIMITER, ind+1)
        except ValueError as e:
            step_i = 0#self.knobs[key](1)
        if ind: # detected range query, range generator protocol implemented
            # Consider alternative implemnetation better in complexity 
            # to indicate ranges: self.opts["range_q"] = True
            self._range_is_active = True
            def range_generator():
                i = self.knobs[key](val[:ind])
                j = self.knobs[key](val[ind+1:step_i if step_i else len(val)])
                step = self.knobs[key](val[step_i+1:] if step_i else 1)
                while i < j:
                    yield i
                    i += step
            return range_generator()
        else: 
            return self.knobs[key](val)
    
    def _raise(self, err):
        print self._pack(err)
    
    def _yield(self, opts): # cycles through all mentioned ranges in cmd 
        if self._generators: # Partial Permutation yield is also available
            try:
                if self.permute_ranges:
                    gen = self._generators_to_permute[self._generators_to_permute[0]]
                    opts[gen] = self._generators[gen].next()
                    if self._generators_to_permute[0] < len(self._generators_to_permute) - 1:
                        self._generators_to_permute[0] += 1  
                    else: 
                        self._generators_to_permute[0] = 1  
                else:
                    for gen in self._generators:
                        opts[gen] = self._generators[gen].next()
            except StopIteration as e:
                opts = None
        else:
            if self.permute_ranges: self._generators_to_permute.append(1) 
            # First index will point to next parameter to be iterated
            for opt in opts:
                if type(opts[opt]) == GeneratorType:
                    self._generators[opt] = opts[opt]
                    if self.permute_ranges: self._generators_to_permute.append(opt)
                    opts[opt] = opts[opt].next()
        return opts


def test_me():
    def func(**opts):
        print "YAY!"
        print opts
    opts = {}
    knobs = ["min_samples_split","a", "b"]
    parsers = [int,]
    flags = ["shrink"]
    msg = "Decision Tree testing. Avl options: {}"
    logger = open("test.txt", 'w')
    cm = CMD_IN(knobs, msg, flags, parsers, verbose=True, executable=func, logger=logger, 
        enable_beep=True, permute_ranges=True)
    n = 100
    for _ in xrange(n):
        cm.input()
        if cm.exit():
            break
        cm.execute()
    # 0 1:10:2 1 4.0:5.7:0.1 2 50

if __name__ == "__main__": test_me()
