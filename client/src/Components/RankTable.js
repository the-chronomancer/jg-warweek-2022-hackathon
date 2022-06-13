import  './table.css'

const RankTable = (props) => {
	const color = {
		0: "#fce434",
		1: "#107fbf",
		2: "#f6110e"
	}
	return (
		<div className="rank-table">
			{
				props?.data?.map( (entry, i) => (
					<div 
						key={`lb-${i}-${entry.name}`}
						className="rank-table-row"
					>
						<div style={{ color: color?.[i] || "black", fontWeight: i < 3 ? "bold" : "normal" }}>{entry.name}</div>
						<div style={{ color: color?.[i] || "black", fontWeight: i < 3 ? "bold" : "normal" }}>{entry.value}</div>
					</div>
				) )
			}
		</div>
	)
}

export default RankTable
