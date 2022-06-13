
// generates react component for outlined bar graph bars 
const BarWithBorder = (borderHeight, borderColor) => {
	return (props) => {
		const { fill, x, y, width, height } = props

		// compute box padding
		const padding = 10
		const nwidth = width - padding
		const nx = x + padding / 2

		return (
			<g>
				<rect x={nx-borderHeight} y={y-borderHeight} width={nwidth+borderHeight*2} height={height+borderHeight} stroke="none" fill={borderColor} />
				<rect x={nx} y={y} width={nwidth} height={height} stroke="none" fill={fill} />
			</g>
		)
	}
}

export default BarWithBorder
