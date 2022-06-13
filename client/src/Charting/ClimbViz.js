import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

import BarWithBorder from './BorderedBar'

const ClimbViz = ({data}) => {

	return (
		<BarChart
			width={500}
			height={300}
			data={data.stats}
			style={{
				fontSize: "12px"
			}}
		>
			<CartesianGrid strokeDasharray="5 5" />
			<XAxis dataKey="label" strokeWidth={2} stroke="#000"/>
			<YAxis strokeWidth={2} stroke="#000"/>
			<Tooltip />
			<Bar dataKey="count" fill="#f6110e" shape={BarWithBorder(4, "#000000")} />
		</BarChart>
	)
}

export default ClimbViz
