import './charts.css'

const Progress = (props) => {
	const done = Math.round(props.done / props.total * 100)

	return (
		<div className="horizontal-progress">
			<div className="progress-done" style={{width: `${done}%`}}>  </div>
			<div className="progress-notdone" style={{width: `${100-done}%`}}>  </div>
		</div>
	)
}

export default Progress
