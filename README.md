# py_cmd_interpret

### 'Plug and Play' easy command line arguments parser and compiler. Best used for parametric tuning and functional testing.
#### Automates testing! Supports Range parameters from cmd for multiple arguments in the form of BEGIN:END:STEP. Permutes through all parameters through generators.
#### Supports completely automatic logging as necessary.
#### Just something I created for ML parametric tuning from cmd. Felt useful. :)
          
#### CONSTRUCTOR PARAMETERS
        
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
