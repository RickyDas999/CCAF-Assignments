import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'

export function CountryMap({ cca3, lat, lng, label }) {
  if (lat == null || lng == null) {
    return (
      <div className="flex h-64 w-full items-center justify-center rounded-lg bg-slate-100 text-sm text-slate-500 dark:bg-slate-800 dark:text-slate-400">
        No coordinates available
      </div>
    )
  }

  return (
    <MapContainer
      key={cca3}
      center={[lat, lng]}
      zoom={5}
      scrollWheelZoom={false}
      className="h-64 w-full rounded-lg md:h-80"
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      <Marker position={[lat, lng]}>
        <Popup>{label}</Popup>
      </Marker>
    </MapContainer>
  )
}
