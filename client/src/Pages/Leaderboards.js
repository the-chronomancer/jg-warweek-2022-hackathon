import RankTable from '../Components/RankTable'
import './leaderboard.css'

const Leaderboards = (props) => {
	const stairLB = [
		{name: "Sean Gibbons", value: "625"},
		{name: "Jacob Coleman", value: "612"},
		{name: "Kevin Holmes", value: "417"},
		{name: "Darrin Jahnel", value: "273"},
		{name: "Jason Jahnel", value: "234"},
		{name: "Jon Keller", value: "232"},
		{name: "Steven Zgalgic", value: "173"},
		{name: "James Murphy", value: "82"},
		{name: "Michael Shirk", value: "65"},
		{name: "Luke Prescott", value: "24"},
		{name: "Johnny Lawrence", value: "21"},
		{name: "Danny LaRusso", value: "17"},
		{name: "John Kreese", value: "13"},
		{name: "Mr Miyagi", value: "9"},
	]

	const challengeLB = [
		{name: "Jacob Coleman", value: "65"},
		{name: "Darrin Jahnel", value: "53"},
		{name: "Jon Keller", value: "49"},
		{name: "Steven Zgalgic", value: "42"},
		{name: "James Murphy", value: "36"},
		{name: "Jason Jahnel", value: "23"},
		{name: "Kevin Holmes", value: "22"},
		{name: "Luke Prescott", value: "15"},
		{name: "Michael Shirk", value: "9"},
		{name: "Sean Gibbons", value: "3"},
	]

	return (
		<div className="leaderboard-content">
			<div className="leaderboard-header">
				<div className="leaderboard-header-cells"> Climbs </div>
				<div className="leaderboard-header-cells"> Challenge </div>
			</div>
			<div className="leaderboard-body">
				<div className="leaderboard-column">
					<RankTable data={stairLB}/>
				</div>
				<div className='leaderboard-column'>
					<RankTable data={challengeLB}/>
				</div>
			</div>
		</div>

	)
}

export default Leaderboards
