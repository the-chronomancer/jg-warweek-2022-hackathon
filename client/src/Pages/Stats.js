import { useState, useEffect } from "react"
import ClimbViz from "../Charting/ClimbViz"
import Numbers from "../Charting/Numbers"
import "./stats.css"
import "../grid.css"

const Stats = (props) => {


	const ranges = {
		"day": 7,
		"week": 4,
		"month": 6,
		"quarter": 4
	}

	const [personalStats, setPersonalStats] = useState(undefined)
	const [jgStats, setJGStats] = useState(undefined)

	const [chartData, setChartData] = useState({stats:[]})
	const [jgChartData, setJGChartData] = useState({stats:[]})

	// grouping is like
	const [grouping, setGrouping] = useState("day")

	useEffect(() => {
		fetch("/prod/api/personalStats")
			.then(resp => resp.json())
			.then(data => {
				setPersonalStats(data)
			})

		fetch("/prod/api/jgStats")
			.then(resp => resp.json())
			.then(data => {
				setJGStats(data)
			})

	}, [])

	useEffect(() => {
		const myparams = new URLSearchParams()
		myparams.append("groupby", grouping)
		myparams.append("range", ranges[grouping])

		const myurl = new URL("/prod/api/myHistorical", window.location)
		myurl.search = myparams

		fetch(myurl)
			.then(resp => resp.json())
			.then( data => {
				setChartData(data)
			} )
		
		const jgparams = new URLSearchParams()
		jgparams.append("groupby", grouping)
		jgparams.append("range", ranges[grouping])

		const jgurl = new URL("/prod/api/jgHistorical", window.location)
		jgurl.search = myparams

		fetch(jgurl)
			.then(resp => resp.json())
			.then( data => {
				setJGChartData(data)
			} )

	}, [grouping])

	return (
		<div className="stats-body">
			<div className="stats-chart-col">
				<div className="row border">
					<div className="col-6" style={{fontWeight: 500}}> My Climbs </div>
					<div className="col-6" style={{fontWeight: 500}}> Jahnel Group </div>
				</div>
				<div className="row border">
					<div className="col-6"> <ClimbViz data={chartData}/> </div>
					<div className="col-6"> <ClimbViz data={jgChartData}/> </div>
				</div>
				<div className="row border">
					<div className="col-6"> <Numbers grouping={grouping} data={personalStats}/> </div>
					<div className="col-6"> <Numbers grouping={grouping} data={jgStats}/> </div>

				</div>
			</div>
		</div>
	)
}

export default Stats
