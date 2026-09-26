/**
 * cityCoordinates.ts
 *
 * Client-side coordinate registry for all 81 V2-supported Indian cities.
 * Maps each canonical city slug (as returned by /locations) to a verified
 * geographic centroid (lat, lon) for the city centre.
 *
 * IMPORTANT: The frontend NEVER calculates distances or feature ratios.
 * These coordinates are passed raw to POST /api/v2/predict.
 * All feature engineering (Haversine distances, area_per_bhk, etc.)
 * is performed exclusively by the backend.
 *
 * Sources: Standard geographic references (Wikipedia, Survey of India).
 */

export interface CityCoord {
  lat: number;
  lon: number;
}

/** Canonical city slug → geographic centroid */
export const CITY_COORDINATES: Record<string, CityCoord> = {
  agra:             { lat: 27.1767,  lon: 78.0081  },
  ahmadnagar:       { lat: 19.0952,  lon: 74.7480  },
  ahmedabad:        { lat: 23.0225,  lon: 72.5714  },
  allahabad:        { lat: 25.4358,  lon: 81.8463  },
  aurangabad:       { lat: 19.8762,  lon: 75.3433  },
  badlapur:         { lat: 19.1557,  lon: 73.2596  },
  bangalore:        { lat: 12.9716,  lon: 77.5946  },
  belgaum:          { lat: 15.8497,  lon: 74.4977  },
  bhiwadi:          { lat: 28.2010,  lon: 76.8602  },
  bhiwandi:         { lat: 19.2812,  lon: 73.0588  },
  bhopal:           { lat: 23.2599,  lon: 77.4126  },
  bhubaneswar:      { lat: 20.2961,  lon: 85.8245  },
  chandigarh:       { lat: 30.7333,  lon: 76.7794  },
  chennai:          { lat: 13.0827,  lon: 80.2707  },
  coimbatore:       { lat: 11.0168,  lon: 76.9558  },
  dehradun:         { lat: 30.3165,  lon: 78.0322  },
  durgapur:         { lat: 23.5204,  lon: 87.3119  },
  ernakulam:        { lat: 9.9816,   lon: 76.2999  },
  faridabad:        { lat: 28.4089,  lon: 77.3178  },
  ghaziabad:        { lat: 28.6692,  lon: 77.4538  },
  goa:              { lat: 15.2993,  lon: 74.1240  },
  'greater-noida':  { lat: 28.4744,  lon: 77.5040  },
  guntur:           { lat: 16.3067,  lon: 80.4365  },
  gurgaon:          { lat: 28.4595,  lon: 77.0266  },
  guwahati:         { lat: 26.1445,  lon: 91.7362  },
  gwalior:          { lat: 26.2183,  lon: 78.1828  },
  haridwar:         { lat: 29.9457,  lon: 78.1642  },
  hyderabad:        { lat: 17.3850,  lon: 78.4867  },
  indore:           { lat: 22.7196,  lon: 75.8577  },
  jabalpur:         { lat: 23.1815,  lon: 79.9864  },
  jaipur:           { lat: 26.9124,  lon: 75.7873  },
  jamshedpur:       { lat: 22.8046,  lon: 86.2029  },
  jodhpur:          { lat: 26.2389,  lon: 73.0243  },
  kalyan:           { lat: 19.2437,  lon: 73.1355  },
  kanpur:           { lat: 26.4499,  lon: 80.3319  },
  kochi:            { lat: 9.9312,   lon: 76.2673  },
  kolkata:          { lat: 22.5726,  lon: 88.3639  },
  kozhikode:        { lat: 11.2588,  lon: 75.7804  },
  lucknow:          { lat: 26.8467,  lon: 80.9462  },
  ludhiana:         { lat: 30.9010,  lon: 75.8573  },
  madurai:          { lat: 9.9252,   lon: 78.1198  },
  mangalore:        { lat: 12.9141,  lon: 74.8560  },
  mohali:           { lat: 30.7046,  lon: 76.7179  },
  mumbai:           { lat: 19.0760,  lon: 72.8777  },
  mysore:           { lat: 12.2958,  lon: 76.6394  },
  nagpur:           { lat: 21.1458,  lon: 79.0882  },
  nashik:           { lat: 19.9975,  lon: 73.7898  },
  'navi-mumbai':    { lat: 19.0330,  lon: 73.0297  },
  navsari:          { lat: 20.9467,  lon: 72.9520  },
  nellore:          { lat: 14.4426,  lon: 79.9865  },
  'new-delhi':      { lat: 28.6139,  lon: 77.2090  },
  noida:            { lat: 28.5355,  lon: 77.3910  },
  palakkad:         { lat: 10.7867,  lon: 76.6548  },
  palghar:          { lat: 19.6967,  lon: 72.7647  },
  panchkula:        { lat: 30.6942,  lon: 76.8606  },
  patna:            { lat: 25.5941,  lon: 85.1376  },
  pondicherry:      { lat: 11.9416,  lon: 79.8083  },
  pune:             { lat: 18.5204,  lon: 73.8567  },
  raipur:           { lat: 21.2514,  lon: 81.6296  },
  rajahmundry:      { lat: 16.9910,  lon: 81.7801  },
  ranchi:           { lat: 23.3441,  lon: 85.3096  },
  satara:           { lat: 17.6805,  lon: 73.9958  },
  shimla:           { lat: 31.1048,  lon: 77.1734  },
  siliguri:         { lat: 26.7271,  lon: 88.3953  },
  solapur:          { lat: 17.6599,  lon: 75.9064  },
  sonipat:          { lat: 28.9288,  lon: 77.0133  },
  surat:            { lat: 21.1702,  lon: 72.8311  },
  thane:            { lat: 19.2183,  lon: 72.9781  },
  thrissur:         { lat: 10.5276,  lon: 76.2144  },
  tirupati:         { lat: 13.6288,  lon: 79.4192  },
  trichy:           { lat: 10.7905,  lon: 78.7047  },
  trivandrum:       { lat: 8.5241,   lon: 76.9366  },
  udaipur:          { lat: 24.5854,  lon: 73.7125  },
  udupi:            { lat: 13.3409,  lon: 74.7421  },
  vadodara:         { lat: 22.3072,  lon: 73.1812  },
  vapi:             { lat: 20.3719,  lon: 72.9113  },
  varanasi:         { lat: 25.3176,  lon: 82.9739  },
  vijayawada:       { lat: 16.5062,  lon: 80.6480  },
  visakhapatnam:    { lat: 17.6868,  lon: 83.2185  },
  vrindavan:        { lat: 27.5794,  lon: 77.6964  },
  zirakpur:         { lat: 30.6456,  lon: 76.8172  },
};

/**
 * Looks up coordinates for a city slug.
 * Returns undefined if the city is not registered.
 */
export function getCityCoord(citySlug: string): CityCoord | undefined {
  return CITY_COORDINATES[citySlug.toLowerCase()];
}
