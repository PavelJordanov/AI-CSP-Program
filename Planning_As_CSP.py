# The output of our program shows the horizon as vertices and the transition between the horizons as edges. Where there are
# k vertices and k - 1 edges, which is aligned with the definition in the assignment. f the horizon is k, we define a CSP
# variable for each STRIPS variable at time step 0 to k, and for each STRIPS action at time step 0 to k - 1. 

# The solution assumes that there are no state constraints such as the robot only being able to hold one thing at a time. 
# Therefore, our solution is such that the robot can hold both the coffee and the mail at the same time. Otherwise, the 
# solution to have it with this state constraint is a simple fix where we would simply remove 1 row from a truth table.

from math import floor
import copy
import sys
import json

# Preconditions Truth Tables

RLOC_RHC_PUC_KEYS = ["RLOC_t", "RHC_t", "PUC"]
RLOC_RHC_PUC = [
    ["cs", True, False],
    ["cs", False, False], 
    ["cs", False, True],
    ["mr", False, False],
    ["mr", True, False],
    ["lab", False, False],
    ["lab", True, False],
    ["off", False, False],
    ["off", True, False],
]

RLOC_RHC_DELC_KEYS = ["RLOC_t", "RHC_t", "DELC"]
RLOC_RHC_DELC = [
    ["cs", False, False],
    ["cs", True, False],
    ["mr", False, False],
    ["mr", True, False],
    ["lab", False, False],
    ["lab", True, False],
    ["off", False, False],
    ["off", True, True],
    ["off", True, False],
]

RLOC_MW_PUM_KEYS = ["RLOC_t", "MW_t", "PUM"]
RLOC_MW_PUM = [
    ["cs", False, False],
    ["cs", True, False],
    ["mr", False, False],
    ["mr", True, True],
    ["mr", True, False],
    ["lab", False, False],
    ["lab", True, False],
    ["off", False, False],
    ["off", True, False],
]

RLOC_RHM_DELM_KEYS = ["RLOC_t", "RHM_t", "DELM"]
RLOC_RHM_DELM = [
    ["cs", False, False],
    ["cs", True, False],
    ["mr", False, False],
    ["mr", True, False],
    ["lab", False, False],
    ["lab", True, False],
    ["off", False, False],
    ["off", True, True],
    ["off", True, False],
]

# Effects Truth Tables

RLOC_t_MOVE_DELC_DELM_PUC_PUM_RLOC_tplus1_KEYS = ["RLOC_t", "MOVE", "DELC", "DELM", "PUC", "PUM", "RLOC_tplus1"]
RLOC_t_MOVE_DELC_DELM_PUC_PUM_RLOC_tplus1 = [
    ["cs", "mc", False, False, False, False, "off"],
    ["cs", "mcc", False, False, False, False, "mr"],
    ["mr", "mc", False, False, False, False, "cs"],
    ["mr", "mcc", False, False, False, False, "lab"],
    ["lab", "mc", False, False, False, False, "mr"],
    ["lab", "mcc", False, False, False, False, "off"],
    ["off", "mc", False, False, False, False, "lab"],
    ["off", "mcc", False, False, False, False, "cs"],

    ["cs", "mc", False, False, True, False, "cs"],
    ["cs", "mcc", False, False, True, False, "cs"],
    ["mr", "mc", False, False, False, True, "mr"],
    ["mr", "mcc", False, False, False, True, "mr"],

    ["off", "mc", True, False, False, False, "off"],
    ["off", "mc", False, True, False, False, "off"],
    ["off", "mc", True, True, False, False, "off"],
    ["off", "mc", False, False, True, False, "off"],
    ["off", "mc", True, False, True, False, "off"],
    ["off", "mc", False, True, True, False, "off"],
    ["off", "mc", True, True, True, False, "off"],
    ["off", "mc", False, False, False, True, "off"],
    ["off", "mc", True, False, False, True, "off"],
    ["off", "mc", False, True, False, True, "off"],
    ["off", "mc", True, True, False, True, "off"],
    ["off", "mc", False, False, True, True, "off"],
    ["off", "mc", True, False, True, True, "off"],
    ["off", "mc", False, True, True, True, "off"],
    ["off", "mc", True, True, True, True, "off"],

    ["off", "mcc", True, False, False, False, "off"],
    ["off", "mcc", False, True, False, False, "off"],
    ["off", "mcc", True, True, False, False, "off"],
    ["off", "mcc", False, False, True, False, "off"],
    ["off", "mcc", True, False, True, False, "off"],
    ["off", "mcc", False, True, True, False, "off"],
    ["off", "mcc", True, True, True, False, "off"],
    ["off", "mcc", False, False, False, True, "off"],
    ["off", "mcc", True, False, False, True, "off"],
    ["off", "mcc", False, True, False, True, "off"],
    ["off", "mcc", True, True, False, True, "off"],
    ["off", "mcc", False, False, True, True, "off"],
    ["off", "mcc", True, False, True, True, "off"],
    ["off", "mcc", False, True, True, True, "off"],
    ["off", "mcc", True, True, True, True, "off"]
]

RHC_t_DELC_PUC_RHC_tplus1_KEYS = ["RHC_t", "DELC", "PUC", "RHC_tplus1"]
RHC_t_DELC_PUC_RHC_tplus1 = [
    [True, True, True, True],
    [True, True, False, False],
    [True, False, True, True],
    [True, False, False, True],
    [False, True, True, False],
    [False, True, False, False],
    [False, False, True, True],
    [False, False, False, False],
]

SWC_t_DELC_SWC_tplus1_KEYS = ["SWC_t", "DELC", "SWC_tplus1"]
SWC_t_DELC_SWC_tplus1 = [
    [True, True, False],
    [True, False, True],
    [False, True, False],
    [False, False, False]
]

MW_t_PUM_MW_tplus1_KEYS = ["MW_t", "PUM", "MW_tplus1"]
MW_t_PUM_MW_tplus1 = [
    [True, False, True],
    [True, True, False],
    [False, False, False],
    [False, True, False]
]

RHM_t_DELM_PUM_DELC_RHM_tplus1_KEYS = ["RHM_t", "DELM", "PUM", "DELC", "RHM_tplus1"]
RHM_t_DELM_PUM_DELC_RHM_tplus1 = [
    [True, True, True, True, False],
    [True, True, False, True, True],
    [True, False, True, True, False],
    [True, False, False, True, False],
    [False, True, True, True, False],
    [False, True, False, True, False],
    [False, False, True, True, False],
    [False, False, False, True, False],

    [True, True, True, False, True],
    [True, True, False, False, False],
    [True, False, True, False, True],
    [True, False, False, False, True],
    [False, True, True, False, False],
    [False, True, False, False, False],
    [False, False, True, False, True],
    [False, False, False, False, False],
]

# GOAL_STATE: RLOC="off", SWC=False

# Time t0
RLOC_t = ["off"]
RHC_t = [False]
SWC_t = [True]
MW_t  = [False]
RHM_t = [True]


MOVE = ["mc", "mcc"]
DELC = [True, False]
PUC  = [True, False]
PUM  = [True, False]
DELM = [True, False]

RLOC_tplus1 = ["cs", "mr", "lab", "off"]
RHC_tplus1 = [True, False]
SWC_tplus1 = [True, False]
MW_tplus1  = [True, False]
RHM_tplus1 = [True, False]

domains = {
    "RLOC_t": RLOC_t,
    "RHC_t": RHC_t,
    "SWC_t": SWC_t,
    "MW_t": MW_t,
    "RHM_t": RHM_t,
    "MOVE": MOVE,
    "DELC": DELC,
    "PUC": PUC,
    "PUM": PUM,
    "DELM": DELM,
    "RLOC_tplus1": RLOC_tplus1,
    "RHC_tplus1": RHC_tplus1,
    "SWC_tplus1": SWC_tplus1,
    "MW_tplus1": MW_tplus1,
    "RHM_tplus1": RHM_tplus1
}

# class for constraints
class Constraint:
    keys   = None
    func   = None
    truths = None

    def __str__(self):
        return f'Constraint {"_".join(self.keys)}'    

c1 = Constraint()
c1.keys = RLOC_RHC_PUC_KEYS
c1.truths = RLOC_RHC_PUC

c2 = Constraint()
c2.keys = RLOC_RHC_DELC_KEYS
c2.truths = RLOC_RHC_DELC

c3 = Constraint()
c3.keys = RLOC_MW_PUM_KEYS
c3.truths = RLOC_MW_PUM

c4 = Constraint()
c4.keys = RLOC_RHM_DELM_KEYS
c4.truths = RLOC_RHM_DELM

c5 = Constraint()
c5.keys = RLOC_t_MOVE_DELC_DELM_PUC_PUM_RLOC_tplus1_KEYS
c5.truths = RLOC_t_MOVE_DELC_DELM_PUC_PUM_RLOC_tplus1

c6 = Constraint()
c6.keys = RHC_t_DELC_PUC_RHC_tplus1_KEYS
c6.truths = RHC_t_DELC_PUC_RHC_tplus1

c7 = Constraint()
c7.keys = SWC_t_DELC_SWC_tplus1_KEYS
c7.truths = SWC_t_DELC_SWC_tplus1

c8 = Constraint()
c8.keys = MW_t_PUM_MW_tplus1_KEYS
c8.truths = MW_t_PUM_MW_tplus1

c9 = Constraint()
c9.keys = RHM_t_DELM_PUM_DELC_RHM_tplus1_KEYS
c9.truths = RHM_t_DELM_PUM_DELC_RHM_tplus1

constraints = [c1, c2, c3, c4, c5, c6, c7, c8, c9]

# Function to check for arc consistency
def acchk(domains, ackey, keys, truths):
    
                
    preserved = []
    removed   = []

    values = domains[ackey]
    
    for val in values:
        
        notFound = True           
        for truth in truths:
            found = True
            
            for i in range(0, len(truth)):
                key = keys[i]
                
                if key == ackey:
                    
                    found &= (truth[i] == val)
                else:
                    
                    found &= (truth[i] in domains[key])
            if found:
                preserved.append(val)
                notFound = False
                break
        if notFound:
            removed.append(val)
        
    
    domains[ackey] = preserved
    return removed

# function to build list of consistent domains
def acdomains(domains, constraints):
    
    consist_domains = copy.deepcopy(domains)

    pipeline = []
    for constraint in constraints:
        for key in constraint.keys:
            pipeline.append((key, constraint))
    
    while pipeline:
        key, constraint = pipeline.pop(0)
        
        
        keys = constraint.func(consist_domains, key, constraint.keys, constraint.truths)
        
        for key in keys:
            for other_constraint in constraints:
                if other_constraint != constraint and key in other_constraint.keys:
                    pipeline.append((key, other_constraint))
        
    return consist_domains

# Function to perform domain splitting
def splitdomains(domains):
    max = 0
    split_key = None
    for key, value in domains.items():
        domain_len = len(value)
        if domain_len > max:
            max = domain_len
            split_key = key 

    if split_key is None:
        return None

    domains1 = {}
    domains2 = {}

    for key, value in domains.items():
        if key == split_key:
            domains1[key] = value[0:floor(len(value)/2)]
            domains2[key] = value[floor(len(value)/2):]
        else:
            domains1[key] = copy.deepcopy(domains[key])
            domains2[key] = copy.deepcopy(domains[key])
    return (domains1, domains2)

#
def process(domains, constraints, csp_solutions):
    consist_domains = acdomains(domains, constraints)
    allOnes = True
    for consist_domain in consist_domains.values():
        if len(consist_domain) == 0:
            return
        elif len(consist_domain) > 1:
            allOnes = False

    if allOnes:
        
        csp_solutions.append(consist_domains)    
        return

    
    domains1, domains2 = splitdomains(consist_domains)
    

    process(domains1, constraints, csp_solutions)
    process(domains2, constraints, csp_solutions)

# Function to check if solution has been found
def isSolved(csp_solutions):
    for csp_solution in csp_solutions:
        if csp_solution["RLOC_tplus1"][0] == "off" and csp_solution["SWC_tplus1"][0] == False:
            return True
    return False

# Function to get list of domains
def getListOfDomains(domains, csp_solutions):
    domains_by_location = {}
    
    for csp_solution in csp_solutions:
        RLOC_t = csp_solution["RLOC_tplus1"][0]
        if RLOC_t not in domains_by_location:
            domains_by_location[RLOC_t] = copy.deepcopy(domains)
            domains_by_location[RLOC_t]["RLOC_t"] = [RLOC_t]
            domains_by_location[RLOC_t]["RHC_t" ] = []
            domains_by_location[RLOC_t]["SWC_t" ] = []
            domains_by_location[RLOC_t]["MW_t"  ] = []
            domains_by_location[RLOC_t]["RHM_t" ] = []

        RHC_t = csp_solution["RHC_tplus1"][0]
        SWC_t = csp_solution["SWC_tplus1"][0]
        MW_t  = csp_solution["MW_tplus1"][0]
        RHM_t = csp_solution["RHM_tplus1"][0]

        if (RHC_t not in domains_by_location[RLOC_t]["RHC_t"]):
            domains_by_location[RLOC_t]["RHC_t"].append(RHC_t)
        if (SWC_t not in domains_by_location[RLOC_t]["SWC_t"]):
            domains_by_location[RLOC_t]["SWC_t"].append(SWC_t)
        if (MW_t not in domains_by_location[RLOC_t]["MW_t"]):
            domains_by_location[RLOC_t]["MW_t"].append(MW_t)
        if (RHM_t not in domains_by_location[RLOC_t]["RHM_t"]):
            domains_by_location[RLOC_t]["RHM_t"].append(RHM_t)

    return list(domains_by_location.values())

# Function to find the path from the start state to the goal state
def find_path(horizon_csp_solutions):
    path = []

    RLOC_t = None
    RHC_t  = None
    SWC_t  = None
    MW_t   = None
    RHM_t  = None

    for csp_solutions in reversed(horizon_csp_solutions):
        for csp_solution in csp_solutions:
            if RLOC_t is None:
                if csp_solution["RLOC_tplus1"][0] == "off" and csp_solution["SWC_tplus1"][0] == False:
                    RLOC_t = csp_solution["RLOC_t"][0]
                    RHC_t  = csp_solution["RHC_t" ][0]
                    SWC_t  = csp_solution["SWC_t" ][0]
                    MW_t   = csp_solution["MW_t"  ][0]
                    RHM_t  = csp_solution["RHM_t" ][0]
                    path.insert(0, csp_solution)
                    break
            else:
                    RLOC_tplus1 = csp_solution["RLOC_tplus1"][0]
                    RHC_tplus1  = csp_solution["RHC_tplus1" ][0]
                    SWC_tplus1  = csp_solution["SWC_tplus1" ][0]
                    MW_tplus1   = csp_solution["MW_tplus1"  ][0]
                    RHM_tplus1  = csp_solution["RHM_tplus1" ][0]

                    if RLOC_t == RLOC_tplus1 and RHC_t == RHC_tplus1 and SWC_t == SWC_tplus1 and MW_t == MW_tplus1 and RHM_t == RHM_tplus1:
                        RLOC_t = csp_solution["RLOC_t"][0]
                        RHC_t  = csp_solution["RHC_t" ][0]
                        SWC_t  = csp_solution["SWC_t" ][0]
                        MW_t   = csp_solution["MW_t"  ][0]
                        RHM_t  = csp_solution["RHM_t" ][0]
                        path.insert(0, csp_solution)
                        break

    return path    
            
for constraint in constraints:
    constraint.func = acchk

def main():
    horizon = 0
    horizon_csp_solutions = []
    list_of_domains = [ copy.deepcopy(domains) ]
    while True:
        csp_solutions = []
        for curr_domains in list_of_domains:
            process(curr_domains, constraints, csp_solutions)

        horizon_csp_solutions.append(csp_solutions)

        if (isSolved(csp_solutions)):
            break
        else:
            horizon += 1
            list_of_domains = getListOfDomains(domains, csp_solutions)
    
    path = find_path(horizon_csp_solutions)
    for idx, step in enumerate(path):
        print(f'Horizon#{idx}\n')
        print(f'{step}\n')
    print(f'Horizon#{len(path)}')

if __name__ == "__main__":
    main()
