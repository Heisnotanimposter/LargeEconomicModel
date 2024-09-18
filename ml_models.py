import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def run_ml_models(news_df):
    X = news_df[['Polarity', 'Subjectivity', 'Fear_Index']]
    y = news_df['Sentiment']
    
    if not X.empty and not y.empty:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Logistic Regression
        model = LogisticRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        st.write(f'Logistic Regression Accuracy: {accuracy}')
        
        # Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        y_pred_rf = rf_model.predict(X_test)
        accuracy_rf = accuracy_score(y_test, y_pred_rf)
        st.write(f'Random Forest Accuracy: {accuracy_rf}')
