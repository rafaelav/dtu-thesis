import pickle

base = "../../plots/"
username= "user_1_sorted"
days_to_consider = 1
filename = base+username+"/"+"list_connected_"+username+"_"+str(days_to_consider)+"days.txt"
pickled_data = pickle.load( open( filename, "rb" ) )
print(pickled_data)
