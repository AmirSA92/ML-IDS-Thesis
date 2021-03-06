import numpy as np
import pandas as pd
from os.path import join
import glob

def read_data(dataroot,file_ending='*.pcap_ISCX.csv'):
    if file_ending==None:
        print("please specify file ending pattern for glob")
        exit()
    print(join(dataroot,file_ending))
    filenames = [i for i in glob.glob(join(dataroot,file_ending))]
    combined_csv = pd.concat([pd.read_csv(f,dtype=object) for f in filenames],sort=False)
    return combined_csv

def load_data(dataroot):
    data = read_data(dataroot,'*.pcap_ISCX.csv')
    num_records,num_features = data.shape
    print("there are {} flow records with {} feature dimension".format(num_records,num_features))
    # Finds and strips whitespaces
    data = data.rename(columns=lambda x: x.strip())
    print('stripped column names')

    df_label = data['Label']
    data = data.drop(columns=['Flow Packets/s','Flow Bytes/s','Label'])
    print('dropped bad columns')
    
    nan_count = data.isnull().sum().sum()
    print('There are {} nan entries'.format(nan_count))
    
    if nan_count>0:
        data.fillna(data.mean(), inplace=True)
        print('filled NAN')

    data = data.astype(float).apply(pd.to_numeric)
    print('converted to numeric')
    
    # Count if there are any missing features
    assert data.isnull().sum().sum()==0, "There should not be any NaN"
    X = data.values
    y = encode_label(df_label.values)
    return (X,y)

# Oversample and undersample the data
def balance_data(X,y,seed):
    np.random.seed(seed)
    unique,counts = np.unique(y,return_counts=True)
    mean_samples_per_class = int(round(np.mean(counts)))
    N,D = X.shape #(number of examples, number of features)

    new_X = np.empty((0,D)) 
    new_y = np.empty((0),dtype=int)
    for i,c in enumerate(unique):
        temp_x = X[y==c]
        indices = np.random.choice(temp_x.shape[0],mean_samples_per_class) # gets `mean_samples_per_class` indices of class `c`
        new_X = np.concatenate((new_X,temp_x[indices]),axis=0) # now we put new data into new_X 
        temp_y = np.ones(mean_samples_per_class,dtype=int)*c
        new_y = np.concatenate((new_y,temp_y),axis=0)
        
    # shuffling
    indices = np.arange(new_y.shape[0])
    np.random.shuffle(indices)
    new_X =  new_X[indices,:]
    new_y = new_y[indices]
    return (new_X,new_y)

# Vectorizing the labels
def encode_label(Y_str):
    labels_d = make_value2index(np.unique(Y_str))
    Y = [labels_d[y_str] for y_str  in Y_str]
    Y = np.array(Y)
    print(Y)
    return np.array(Y)

def make_value2index(attacks):
    #make dictionary
    attacks = sorted(attacks)
    d = {}
    counter=0
    for attack in attacks:
        d[attack] = counter
        counter+=1
    return d

# The normalization process
def normalize(data):
        data = data.astype(np.float32)
       
        eps = 1e-15

        mask = data==-1
        data[mask]=0
        mean_i = np.mean(data,axis=0)
        min_i = np.min(data,axis=0)
        max_i = np.max(data,axis=0)

        r = max_i-min_i+eps
        data = (data-mean_i)/r  # zero centered 

        #deal with missing features -1
        data[mask] = 0        
        return data
