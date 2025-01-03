import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import time
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve, auc
from sklearn.datasets import load_breast_cancer
import joblib

def main():
    st.set_page_config(page_title='ONCO DETECT', page_icon='tumor_icon.png', layout='wide', initial_sidebar_state='auto')
    col1, col2 = st.columns([2,8])
    col2.title('Breast Cancer Detection')
    col1.image('tumor_icon.png',width=100)
    st.sidebar.title('ONCO DETECT')
    st.markdown('Cancer is Malignant or Benign? ')
    navigation = st.sidebar.radio('VIEW', ('Data Analysis', 'Training', 'Predict'))

    # Function to load saved models
    def load_saved_models():
        import os
        model_dir = 'saved_models/'
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        models = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
        return models
    
    @st.cache_data(persist=True)
    def load_data():
        cancer = load_breast_cancer()
        df = pd.DataFrame(cancer.data,columns=cancer.feature_names)
        df['target'] = cancer.target    
        labelencoder=LabelEncoder()
        for col in df.columns:
            df[col] = labelencoder.fit_transform(df[col])
        return df
    
    @st.cache_data(persist=True)
    def split(df):
        y = df['target']
        x = df.drop(columns=['target'])
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        return x_train, x_test, y_train, y_test
    
   
    
    def plot_metrics(metrics_list):
        if 'Confusion Matrix' in metrics_list:
            st.subheader("Confusion Matrix")
            cm = confusion_matrix(y_test, y_pred)
            fig,ax = plt.subplots()
            sns.heatmap(cm, annot = True)
            # plot_confusion_matrix(model, x_test, y_test, display_labels=class_names)
            ax.figure.savefig('file.png')
            st.pyplot(fig)
        if 'Precision-Recall Curve' in metrics_list:
            st.subheader('Precision-Recall Curve')
            
            precision, recall, thresholds = precision_recall_curve(y_test, y_pred)

            fig = px.area(
                x=recall, y=precision,
                title=f'Precision-Recall Curve (AUC={auc(precision, recall):.4f})',
                labels=dict(x='Recall', y='Precision'),
                width=700, height=500
                )
            fig.add_shape(
                type='line', line=dict(dash='dash'),
                x0=0, x1=1, y0=1, y1=0
                )
            fig.update_yaxes(scaleanchor="x", scaleratio=1)
            fig.update_xaxes(constrain='domain')
            st.write(fig)
            
            
        if 'ROC Curve' in metrics_list:
            fpr, tpr, thresholds = roc_curve(y_test, y_pred)

            fig = px.area(
               x=fpr, y=tpr,
               title=f'ROC Curve (AUC={auc(fpr, tpr):.4f})',
               labels=dict(x='False Positive Rate', y='True Positive Rate'),
               width=700, height=500
               )       
            fig.add_shape(
                type='line', line=dict(dash='dash'),
                x0=0, x1=1, y0=0, y1=1
                )

            fig.update_yaxes(scaleanchor="x", scaleratio=1)
            fig.update_xaxes(constrain='domain')
            st.write(fig)
        
        if 'Training and Test accuracies' in metrics_list:
            mal_train_X = x_train[y_train==0]
            mal_train_y = y_train[y_train==0]
            ben_train_X = x_train[y_train==1]
            ben_train_y = y_train[y_train==1]
            
            mal_test_X = x_test[y_test==0]
            mal_test_y = y_test[y_test==0]
            ben_test_X = x_test[y_test==1]
            ben_test_y = y_test[y_test==1]
            
            scores = [model.score(mal_train_X, mal_train_y), model.score(ben_train_X, ben_train_y), model.score(mal_test_X, mal_test_y), model.score(ben_test_X, ben_test_y)]

            fig,ax = plt.subplots()
        
    # Plot the scores as a bar chart
            bars = plt.bar(np.arange(4), scores, color=['#4c72b0','#4c72b0','#55a868','#55a868'])

    # directly label the score onto the bars
            for bar in bars:
                height = bar.get_height()
                plt.gca().text(bar.get_x() + bar.get_width()/2, height*.90, '{0:.{1}f}'.format(height, 2), ha='center', color='w', fontsize=11)

    # remove all the ticks (both axes), and tick labels on the Y axis
            plt.tick_params(top='off', bottom='off', left='off', right='off', labelleft='off', labelbottom='on')

    # remove the frame of the chart
            for spine in plt.gca().spines.values():
                spine.set_visible(False)

            plt.xticks([0,1,2,3], ['Malignant\nTraining', 'Benign\nTraining', 'Malignant\nTest', 'Benign\nTest'], alpha=0.8);
            plt.title('Training and Test Accuracies for Malignant and Benign Cells', alpha=0.8)
            ax.xaxis.set_tick_params(length=0)
            ax.yaxis.set_tick_params(length=0)
            ax.figure.savefig('file1.png')
            st.pyplot(fig)
            
    df = load_data()
    class_names = ['malignant', 'benign']
    
    
###------------------DATA ANAlYSIS--------------------------       
    if navigation == 'Data Analysis':
        
        
        
        if st.sidebar.checkbox("Show Raw Data", False):
            st.subheader('Breast Cancer Dataset')
            
            st.dataframe(df)
            
        if st.sidebar.checkbox("Show Features", False):
            cancer = load_breast_cancer()
            st.subheader('Features')
            features = pd.DataFrame(cancer.feature_names)
            features.columns = ['Features']
            st.dataframe(features)
            
    
        plots =  st.sidebar.multiselect("Plots", ('Scatter Matrix', 'Number of Malignant and Benign','Heatmap','Mean radius vs Mean area','Mean smoothness vs Mean area'))
        
        
        if st.sidebar.button("Plot", key='plotss'):
            with st.spinner('Wait for it...'):
                time.sleep(5)
 
            if 'Number of Malignant and Benign' in plots:
                st.subheader("Malignant and Benign Count")
                fig,ax = plt.subplots()
                
                ma = len(df[df['target']==1])
                be = len(df[df['target']==0])
                count=[ma,be]
                bars = plt.bar(np.arange(2), count, color=['#000099','#ffff00'])
                ##show value in bars
                for bar in bars:
                    height = bar.get_height()
                    plt.gca().text(bar.get_x() + bar.get_width()/2, height*.90, '{0:.{1}f}'.format(height, 2), ha='center', color='black', fontsize=11)
                plt.tick_params(top='off', bottom='off', left='off', right='off', labelleft='on', labelbottom='on')
                for spine in plt.gca().spines.values():
                    spine.set_visible(False)
                plt.xticks(ticks=[0,1])
                ax.set_ylabel('Count')
                ax.set_xlabel('Target')
                ##remove dashes from frame
                ax.xaxis.set_tick_params(length=0)
                ax.yaxis.set_tick_params(length=0)
                st.pyplot(fig)
                
            
            if 'Scatter Matrix' in plots:
                st.subheader("Scatter Matrix")
                fig = px.scatter_matrix(df,dimensions=['mean radius','mean texture','mean perimeter','mean area','mean smoothness'],color="target",width = 800,height = 700)
                st.write(fig)
            
            if 'Heatmap' in plots:
                st.subheader("Heatmap")
                fig=plt.figure(figsize = (30,20))
                hmap=sns.heatmap(df.drop(columns=['target']).corr(), annot = True,cmap= 'Blues',annot_kws={"size": 18})
                hmap.set_xticklabels(hmap.get_xmajorticklabels(), fontsize = 25)
                hmap.set_yticklabels(hmap.get_ymajorticklabels(), fontsize = 25)
                st.pyplot(fig)
            if 'Mean radius vs Mean area' in plots:
                st.subheader('Cancer Radius and Area')
                fig = plt.figure()
                sns.scatterplot(x=df['mean radius'],y = df['mean area'],hue = df['target'],palette=['#000099','#ffff00'])
                st.pyplot(fig)
            if 'Mean smoothness vs Mean area' in plots:
                st.subheader('Cancer Smoothness and Area')
                fig = plt.figure()
                sns.scatterplot(x=df['mean smoothness'],y = df['mean area'],hue = df['target'],palette=['#000099','#ffff00'])
                st.pyplot(fig)
        
###---------------training----------------------
    if navigation == 'Training':
        
        x_train, x_test, y_train, y_test = split(df)
        if st.sidebar.checkbox("Show X_train/Y_train", False):
            col = st.columns([8,2])
            col[0].subheader('X_train')
            col[0].dataframe(x_train)
            col[1].subheader('Y_train')
            col[1].dataframe(y_train)
        
        st.sidebar.subheader("Choose Classifier")
        classifier = st.sidebar.selectbox("Classifier", ("Support Vector Machine (SVM)", "Logistic Regression", "Random Forest", 'KNN', 'Decision Tree', 'Gaussian Naive Bayes'))
        # classifier = st.sidebar.selectbox("Classifier", ("Logistic Regression", "Random Forest", 'KNN'))

        
        if classifier == 'Support Vector Machine (SVM)':
            st.sidebar.subheader("Model Hyperparameters")
            #choose parameters
            C = st.sidebar.number_input("C (Regularization parameter)", 0.01, 10.0, step=0.01, key='C_SVM')
            kernel = st.sidebar.radio("Kernel", ("rbf", "linear"), key='kernel')
            gamma = st.sidebar.radio("Gamma (Kernel Coefficient)", ("scale", "auto"), key='gamma')

            metrics = st.sidebar.multiselect("Metrics to Plot", ('Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve','Training and Test accuracies'))
        
            if st.sidebar.button("Classify", key='classify'):
                st.subheader("Support Vector Machine (SVM) Results")
                model = SVC(C=C, kernel=kernel, gamma=gamma)
                model.fit(x_train, y_train)
                accuracy = model.score(x_test, y_test)
                y_pred = model.predict(x_test)
                st.write(f"Accuracy: {accuracy:.2f}")
                st.write(f"Precision: {precision_score(y_test, y_pred, labels=class_names):.2f}")
                st.write(f"Recall: {recall_score(y_test, y_pred, labels=class_names):.2f}")
                plot_metrics(metrics)

                joblib.dump(model, 'saved_models/svm_model.pkl')
                st.sidebar.success("Model saved as svm_model.pkl!")
    
        if classifier == 'Logistic Regression':
            st.sidebar.subheader("Model Hyperparameters")
            C = st.sidebar.number_input("C (Regularization parameter)", 0.01, 10.0, step=0.01, key='C_LR')
            max_iter = st.sidebar.slider("Maximum number of iterations", 100, 500, key='max_iter')
            
            metrics = st.sidebar.multiselect("Metrics to Plot", ('Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve','Training and Test accuracies'))
            
            if st.sidebar.button("Classify", key='classify'):
                st.subheader("Logistic Regression Results")
                model = LogisticRegression(C=C, penalty='l2', max_iter=max_iter)
                model.fit(x_train, y_train)
                accuracy = model.score(x_test, y_test)
                y_pred = model.predict(x_test)
                st.write(f"Accuracy: {accuracy:.2f}")
                st.write(f"Precision: {precision_score(y_test, y_pred, labels=class_names):.2f}")
                st.write(f"Recall: {recall_score(y_test, y_pred, labels=class_names):.2f}")
                plot_metrics(metrics)

                joblib.dump(model, 'saved_models/lr_model.pkl')
                st.sidebar.success("Model saved as lr_model.pkl!")
                
        if classifier == 'Random Forest':
            st.sidebar.subheader("Model Hyperparameters")
            n_estimators = st.sidebar.number_input("The number of trees in the forest", 100, 5000, step=10, key='n_estimators')
            max_depth = st.sidebar.number_input("The maximum depth of the tree", 1, 20, step=1, key='max_depth')
            bootstrap = True if st.sidebar.radio("Bootstrap samples when building trees", ('True', 'False'), key='bootstrap')=='True' else False
            metrics = st.sidebar.multiselect("Metrics to Plot", ('Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve','Training and Test accuracies'))
            
            if st.sidebar.button("Classify", key='classify'):
                st.subheader("Random Forest Results")
                model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, bootstrap=bootstrap, n_jobs=-1)
                model.fit(x_train, y_train)
                accuracy = model.score(x_test, y_test)
                y_pred = model.predict(x_test)
                st.write(f"Accuracy: {accuracy:.2f}")
                st.write(f"Precision: {precision_score(y_test, y_pred, labels=class_names):.2f}")
                st.write(f"Recall: {recall_score(y_test, y_pred, labels=class_names):.2f}")
                plot_metrics(metrics)

                joblib.dump(model, 'saved_models/rf_model.pkl')
                st.sidebar.success("Model saved as rf_model.pkl!")
                
        if classifier == 'KNN':
            st.sidebar.subheader("Model Hyperparameters")
            n_neighbors = st.sidebar.number_input("Number of neighbors", 1, 100, step=1, key='n_neighbors')
            
            metrics = st.sidebar.multiselect("Metrics to Plot", ('Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve','Training and Test accuracies'))

            if st.sidebar.button("Classify", key='classify'):
                st.subheader("KNN Results")
                model = KNeighborsClassifier(n_neighbors = n_neighbors )
                model.fit(x_train, y_train)
                accuracy = model.score(x_test, y_test)
                y_pred = model.predict(x_test)
                st.write(f"Accuracy: {accuracy:.2f}")
                st.write(f"Precision: {precision_score(y_test, y_pred, labels=class_names):.2f}")
                st.write(f"Recall: {recall_score(y_test, y_pred, labels=class_names):.2f}")
                plot_metrics(metrics)

                joblib.dump(model, 'saved_models/knn_model.pkl')
                st.sidebar.success("Model saved as knn_model.pkl!")
                
        if classifier == 'Decision Tree':
            st.sidebar.subheader("Model Hyperparameters")
            
            max_depth = st.sidebar.number_input("The maximum depth of the tree", 1, 20, step=1, key='max_depth')
            criterion = st.sidebar.radio("Criterion", ("gini", "entropy"), key='criterion')
            splitter = st.sidebar.radio("Splitter", ("best", "random"), key='splitter')
            metrics = st.sidebar.multiselect("Metrics to Plot", ('Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve','Training and Test accuracies'))
            
            if st.sidebar.button("Classify", key='classify'):
                st.subheader("Decision Tree Results")
                model = DecisionTreeClassifier(max_depth= max_depth, criterion= criterion, splitter= splitter )
                model.fit(x_train, y_train)
                accuracy = model.score(x_test, y_test)
                y_pred = model.predict(x_test)
                st.write(f"Accuracy: {accuracy:.2f}")
                st.write(f"Precision: {precision_score(y_test, y_pred, labels=class_names):.2f}")
                st.write(f"Recall: {recall_score(y_test, y_pred, labels=class_names):.2f}")
                plot_metrics(metrics)

                joblib.dump(model, 'saved_models/dt_model.pkl')
                st.sidebar.success("Model saved as dt_model.pkl!")
                
        if classifier == 'Gaussian Naive Bayes':
            st.sidebar.subheader("Model Hyperparameters")
        
        
            metrics = st.sidebar.multiselect("Metrics to Plot", ('Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve','Training and Test accuracies'))

            if st.sidebar.button("Classify", key='classify'):
                st.subheader("Gaussian Naive Bayes Results")
                model = GaussianNB()
                model.fit(x_train, y_train)
                accuracy = model.score(x_test, y_test)
                y_pred = model.predict(x_test)
                st.write(f"Accuracy: {accuracy:.2f}")
                st.write(f"Precision: {precision_score(y_test, y_pred, labels=class_names):.2f}")
                st.write(f"Recall: {recall_score(y_test, y_pred, labels=class_names):.2f}")
                plot_metrics(metrics)

                joblib.dump(model, 'saved_models/gnb_model.pkl')
                st.sidebar.success("Model saved as gnb_model.pkl!")   

    if navigation == 'Predict':
        st.sidebar.subheader("Model Prediction")
        
        # Load available models
        models = load_saved_models()
        if len(models) == 0:
            st.error("No saved models found! Please train and save a model first.")
        else:
            # Model selection
            selected_model = st.sidebar.selectbox("Choose a model", models)
            
            # Input form for predictions
            st.subheader("Input Features")
            feature_inputs = {}
            for feature in load_breast_cancer().feature_names:
                feature_inputs[feature] = st.number_input(feature, value=0.0, step=0.1)
            
            # Predict button
            if st.button("Predict"):
                try:
                    # Load the selected model
                    model_path = f'saved_models/{selected_model}'
                    model = joblib.load(model_path)
                    
                    # Prepare the input data
                    input_data = np.array([list(feature_inputs.values())]).reshape(1, -1)
                    
                    # Perform prediction
                    prediction = model.predict(input_data)
                    pred_proba = model.predict_proba(input_data) if hasattr(model, 'predict_proba') else None
                    
                    # Display results
                    st.write(f"Prediction: {'Malignant' if prediction[0] == 0 else 'Benign'}")
                    if pred_proba is not None:
                        st.write(f"Probability: {pred_proba[0][0]:.2f}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")          
    
if __name__ == '__main__':
    main()
