import React, { useState, useEffect } from 'react'
import MapComponent from './components/MapComponent'
import cityData from './data/city_aqi_data.json'
import './styles/App.css'

function App() {

  const [states, setStates] = useState([])
  const [festivalPeriods, setFestivalPeriods] = useState([])
  const [seasonList, setSeasonList] = useState([])

  const [selectedState, setSelectedState] = useState('')
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [mode, setMode] = useState('festival') // festival | season

  const [mapData, setMapData] = useState([])

  // Load states
  useEffect(() => {
    setStates(Object.keys(cityData).sort())
  }, [])

  // When state changes → load festivals & seasons
  useEffect(() => {
    if (!selectedState) return

    const festivals = new Set()
    const seasons = new Set()

    Object.values(cityData[selectedState]).forEach(city => {
      Object.keys(city.festival_aqi || {}).forEach(f => festivals.add(f))
      Object.keys(city.season_aqi || {}).forEach(s => seasons.add(s))
    })

    setFestivalPeriods([...festivals].sort())
    setSeasonList([...seasons].sort())

    setSelectedPeriod('')
    setMapData([])
  }, [selectedState])

  // Prepare map data → ALL CITIES OF STATE
  useEffect(() => {
    if (!selectedState || !selectedPeriod) return

    const cities = []

    Object.entries(cityData[selectedState]).forEach(([cityName, cityInfo]) => {

      const source =
        mode === 'festival'
          ? cityInfo.festival_aqi
          : cityInfo.season_aqi

      if (source && source[selectedPeriod]) {
        const aqiData = source[selectedPeriod]

        cities.push({
          city: cityName,
          latitude: cityInfo.latitude,
          longitude: cityInfo.longitude,
          aqi: aqiData.avg_aqi,
          aqi_category: aqiData.category,
          data_points: aqiData.data_points
        })
      }
    })

    setMapData(cities)
  }, [selectedState, selectedPeriod, mode])

  // AQI color logic
  const getAqiColor = (aqi) => {
    if (!aqi) return '#666'
    if (aqi <= 50) return '#00e400'
    if (aqi <= 100) return '#ffff00'
    if (aqi <= 200) return '#ff7e00'
    if (aqi <= 300) return '#ff0000'
    if (aqi <= 400) return '#99004c'
    return '#7e0023'
  }

  return (
    <div className="app">

      <header className="app-header">
        <h1>🌍 India AQI Map</h1>
        <p>State-wise City AQI Visualization</p>
      </header>

      <div className="controls">

        {/* Festival / Season Mode */}
        <div className="dropdown-group">
          <label>View Type:</label>
          <select
            value={mode}
            onChange={(e) => {
              setMode(e.target.value)
              setSelectedPeriod('')
              setMapData([])
            }}
          >
            <option value="festival">Festival-wise AQI</option>
            <option value="season">Season-wise AQI</option>
          </select>
        </div>

        {/* State */}
        <div className="dropdown-group">
          <label>Select State:</label>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
          >
            <option value="">Choose a state</option>
            {states.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>

        {/* Season / Festival */}
        {selectedState && (
          <div className="dropdown-group">
            <label>{mode === 'festival' ? 'Festival Period:' : 'Season:'}</label>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
            >
              <option value="">
                Choose {mode === 'festival' ? 'festival period' : 'season'}
              </option>

              {(mode === 'festival' ? festivalPeriods : seasonList).map(item => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </div>
        )}

      </div>

      {/* Map */}
      <div className="map-section">
        {selectedState && selectedPeriod && (
          <h2 className="map-title">
            📍 {selectedState} — {selectedPeriod}
            <span className="city-count"> ({mapData.length} cities)</span>
          </h2>
        )}

        <MapComponent
          cityData={mapData}
          getAqiColor={getAqiColor}
        />
      </div>

    </div>
  )
}

export default App






{/*import React, { useState, useEffect } from 'react'
import MapComponent from './components/MapComponent'
import cityData from './data/city_aqi_data.json'  // Import the preprocessed data
import './styles/App.css'

function App() {
  const [states, setStates] = useState([])
  const [selectedState, setSelectedState] = useState('')
  const [festivalPeriods, setFestivalPeriods] = useState([])
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [mapData, setMapData] = useState([])

  // Load states from the JSON data
  useEffect(() => {
    const stateNames = Object.keys(cityData).sort()
    setStates(stateNames)
  }, [])

  // When state changes, update festival periods
  useEffect(() => {
    if (selectedState && cityData[selectedState]) {
      const periods = new Set()
      
      Object.values(cityData[selectedState]).forEach(city => {
        Object.keys(city.festival_aqi).forEach(period => {
          periods.add(period)
        })
      })
      
      setFestivalPeriods(Array.from(periods).sort())
      setSelectedPeriod('')
      setMapData([])
    }
  }, [selectedState])

  // When festival period changes, prepare map data
  useEffect(() => {
    if (selectedState && selectedPeriod && cityData[selectedState]) {
      const cities = []
      
      Object.entries(cityData[selectedState]).forEach(([cityName, cityInfo]) => {
        if (cityInfo.festival_aqi[selectedPeriod]) {
          const aqiData = cityInfo.festival_aqi[selectedPeriod]
          cities.push({
            city: cityName,
            latitude: cityInfo.latitude,
            longitude: cityInfo.longitude,
            aqi: aqiData.avg_aqi,
            aqi_category: aqiData.category,
            data_points: aqiData.data_points
          })
        }
      })
      
      setMapData(cities)
    }
  }, [selectedState, selectedPeriod])

  const getAqiColor = (aqi) => {
    if (!aqi) return '#666'
    if (aqi <= 50) return '#00e400'
    if (aqi <= 100) return '#ffff00'
    if (aqi <= 200) return '#ff7e00'
    if (aqi <= 300) return '#ff0000'
    if (aqi <= 400) return '#99004c'
    return '#7e0023'
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌍 India Air Quality Index Map</h1>
        <p>Visualize average AQI across cities and festival seasons</p>
      </header>

      <div className="controls">
        <div className="dropdown-group">
          <label>Select State:</label>
          <select 
            value={selectedState} 
            onChange={(e) => setSelectedState(e.target.value)}
          >
            <option value="">Choose a state</option>
            {states.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>

        {festivalPeriods.length > 0 && (
          <div className="dropdown-group">
            <label>Festival Period:</label>
            <select 
              value={selectedPeriod} 
              onChange={(e) => setSelectedPeriod(e.target.value)}
            >
              <option value="">Choose festival period</option>
              {festivalPeriods.map(period => (
                <option key={period} value={period}>{period}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="map-section">
        {selectedState && selectedPeriod && (
          <h2 className="map-title">
            📍 {selectedState} - {selectedPeriod}
            <span className="city-count"> ({mapData.length} cities)</span>
          </h2>
        )}
        
        <MapComponent 
          cityData={mapData} 
          getAqiColor={getAqiColor}
        />
        
        <div className="legend">
          <h4>AQI Color Legend:</h4>
          <div className="legend-items">
            {['Good (0-50)', 'Satisfactory (51-100)', 'Moderate (101-200)', 
              'Poor (201-300)', 'Very Poor (301-400)', 'Severe (401-500)'].map((item, index) => (
              <div key={item} className="legend-item">
                <span 
                  className="color-dot" 
                  style={{backgroundColor: getAqiColor(
                    item === 'Good (0-50)' ? 25 :
                    item === 'Satisfactory (51-100)' ? 75 :
                    item === 'Moderate (101-200)' ? 150 :
                    item === 'Poor (201-300)' ? 250 :
                    item === 'Very Poor (301-400)' ? 350 : 450
                  )}}
                ></span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App */}