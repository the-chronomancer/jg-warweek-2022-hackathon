import './App.css'
import './grid.css'

import {
	BrowserRouter,
	Routes,
	Route,
} from "react-router-dom"

import Stats from './Pages/Stats'
import Leaderboards from './Pages/Leaderboards'
import Challenges from './Pages/Challenges'
import Passport from './Pages/Passport'

import Progress from './Charting/Progress'
import { useEffect, useState } from 'react'

function App() {

	const pages = {
	  "Day": "/stats",
	  "Week": "/leaderboards",
	  "Month": "/challenges",
	  "Quarter": "/passport"
	}

	const groupings = [
		"Day",
		"Week",
		"Month",
		"Quarter"
	]

	const [progress, setProgress] = useState("0")
	const [timescale, setTimescale] = useState("day")

	useEffect(() => {
		fetch("/prod/api/total")
			.then( resp => resp.json() )
			.then( data => { setProgress(data?.count || "0") } )
	}, [])

	return (
		<div className='app'>
			{/* header */}
			<div className='header row'>
				<h1 className='col-4'>EffingLegs!</h1>
				<div className='col-4'>
					<BrowserRouter>
						<Routes>
							<Route path="/" element={null}/>
							<Route path="/stats" element={<h2>Stats</h2>}/>
							<Route path="/leaderboards" element={<h2>Leaderboards</h2>}/>
							<Route path="/challenges" element={<h2>Challenges</h2>}/>
							<Route path="/passport" element={<h2>Passport</h2>}/>
						</Routes>
					</BrowserRouter>
				</div>
				<div className='col-4'>
					<Progress done={parseInt(progress)} total={100} />
				</div>
			</div>


			{/* page content */}
			<div style={{width: "100%"}}>
				<BrowserRouter>
					<Routes>
						<Route path="/" element={null}/>
						<Route path="/stats" element={<Stats grouping={timescale}/>}/>
						<Route path="/leaderboards" element={<Leaderboards/>}/>
						<Route path="/challenges" element={<Challenges/>}/>
						<Route path="/passport" element={<Passport/>}/>
					</Routes>
				</BrowserRouter>
			</div>

			{/* navbar! */}
			<div className='overlay'> 
				<div className='menu'> 
					{
						groupings.map((time) => (
							// <a className="menuitem" href={link}>{page}</a>
							<span className="menuitem" onClick={()=>{setTimescale(time)}}>{time}</span>

						))
					}
				</div>
			</div>
		</div>
	)
}

export default App
