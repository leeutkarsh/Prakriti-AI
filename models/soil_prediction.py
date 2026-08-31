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
    # Prepare input data
    input_location = np.array([[latitude, longitude]])
    
    # Scale the input
    input_scaled = soil_scaler.transform(input_location)
    
    # Make predictions for each soil characteristic
    predictions = {}
    
    for level in soil_levels:
        # Predict encoded level
        level_encoded = soil_models[level].predict(input_scaled)[0]
        
        # Decode to get the actual level name
        level_name = soil_encoders[level].inverse_transform([level_encoded])[0]
        
        # Store in predictions dictionary
        predictions[level] = level_name
    
    return predictions
