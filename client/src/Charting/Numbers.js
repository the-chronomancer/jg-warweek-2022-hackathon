import "./charts.css"

const Numbers = (props) => {
	const grouping = props?.grouping
	const climbs = props?.data?.[grouping]
	const conversion = props?.data?.conversion
	const stairs = climbs * conversion

	const groupingDisplay = {
		"day": "Today",
		"week": "This Week",
		"month": "This Month",
		"quarter": "This Quarter"
	}

	return (
		<div className="numbers">
			<div className="numbers-row"> 
				<div> {groupingDisplay[props?.grouping] || "-"}</div> 
				<div> {props?.data?.[grouping] || "-"} Climbs </div> 
			</div>

			<div className="numbers-row"> 
				<div> </div> 
				<div> {stairs || "-"} Stairs</div>
			</div>			
		</div>
	)
}

export default Numbers
