import React from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default markers
import L from 'leaflet'
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

const MapComponent = ({ cityData, getAqiColor, loading }) => {
  if (loading) {
    return (
      <div className="map-loading">
        <div className="spinner"></div>
        <p>Loading map data...</p>
      </div>
    )
  }

  if (!cityData || cityData.length === 0) {
    return (
      <div className="map-placeholder">
        <h3>🌍 Select State & Festival Period</h3>
        <p>Choose from dropdowns to view AQI data on map</p>
      </div>
    )
  }

  // Create colored circle markers
  const createCustomIcon = (aqi) => {
    const color = getAqiColor(aqi)
    return L.divIcon({
      className: 'custom-marker',
      html: `<div style="
        background-color: ${color};
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      "></div>`,
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    })
  }

  return (
    <div className="leaflet-map-container">
      <MapContainer
        center={[22.9734, 78.6569]}
        zoom={5}
        style={{ height: "500px", width: "100%" }}
        className="leaflet-map"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {cityData.map((city, index) => {
          if (!city.latitude || !city.longitude) return null
          
          return (
            <Marker
              key={index}
              position={[city.latitude, city.longitude]}
              icon={createCustomIcon(city.aqi)}
            >
              <Popup>
                <div className="popup-content">
                  <h4>{city.city}</h4>
                  <p><strong>AQI:</strong> {city.aqi || 'N/A'}</p>
                  <p><strong>Category:</strong> {city.aqi_category}</p>
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}

export default MapComponent