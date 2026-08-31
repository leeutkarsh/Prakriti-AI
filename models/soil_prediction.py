def predict_soil_characteristics(latitude, longitude):
    """
    Predict soil characteristics (N, P, K, pH levels) based on location
    
    Parameters:
    -----------
    latitude : float
        Latitude coordinate
    longitude : float
        Longitude coordinate
        
    Returns:
    --------
    dict
        Dictionary with predicted soil characteristics
    """
    input_location = np.array([[latitude, longitude]])
    
    input_scaled = soil_scaler.transform(input_location)
    
    predictions = {}
    
    for level in soil_levels:
        level_encoded = soil_models[level].predict(input_scaled)[0]
        level_name = soil_encoders[level].inverse_transform([level_encoded])[0]
        predictions[level] = level_name
    
    return predictions
