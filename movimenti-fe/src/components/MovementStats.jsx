import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, LabelList, Cell, Rectangle } from 'recharts';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import { useMediaQuery } from 'react-responsive'
import { t } from "@lingui/macro";
// import { colors } from '../constants';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    let valString = `${parseFloat(payload[0].payload.sum).toFixed(2)}`;
    if(payload[0].payload.percent){
      valString += ` (${parseFloat(payload[0].value).toFixed(1)}%)`;
    }
    return (
      <div className="custom-tooltip">
        <p className="label">{`${label}`}</p>
        <p>{valString}</p>
      </div>
    );
  }

  return null;
};

const MovementsStats = ({data, categories}) => {
    const percent_cutin = 0.02;
    let earningData = {
      earnings: [],
    };
    let expensesData = {
      expenses: [],
    };
    let totalsData = [];
    let incomes = 0;
    let outcomes = 0;
    let statsCategories = {};
    if(data?.filtered?.movements) {
      let outliers = {
        incomes: {category: t`Other in.` + ` (<${100*percent_cutin}%)`, sum: 0, percent: 0, direction: 1},
        outcomes: {category: t`Other out.` + ` (<${100*percent_cutin}%)`, sum: 0, percent: 0, direction: -1},
      }
      for (const movement of data.filtered.movements) {
        if(movement.amount == 0.0){ // filter out BALANCE-type movements
          continue
        }
        // if(slice){
        //   const mDate = new Date(movement.date);
        //   if(mDate < slice.minDate || mDate > slice.maxDate){
        //     continue;
        //   }
        // }
        if(movement.amount>0){   
          incomes += movement.abs_amount;
        }else {
          outcomes += movement.abs_amount;
        }
        const cat = categories.find((cat)=> cat.id === movement.category);
        if(cat){
          if(cat.category in statsCategories){
            statsCategories[cat.category].sum += movement.abs_amount
          }else{
            statsCategories[cat.category] = {...cat, "sum": movement.abs_amount};
          }
        }
      }
      for (const catName in statsCategories) {
        const cat = statsCategories[catName];
        let percent = 0.;
        if(cat.direction === 1) {
          percent = cat.sum/incomes;
          const newitem = {...cat, "percent": percent};
          if(percent>=percent_cutin){
            earningData.earnings.push(newitem);
          }else{
            outliers.incomes.sum += newitem.sum;
            outliers.incomes.percent += newitem.sum;
          }
        }else if(cat.direction === -1){
          percent = cat.sum/outcomes;
          const newitem = {...cat, "percent": percent};
          if(percent>=percent_cutin){
            expensesData.expenses.push(newitem)
          }else{
            outliers.outcomes.sum += newitem.sum;
            outliers.outcomes.percent += newitem.percent;
          }
        }
      }
      earningData.earnings.sort((a,b)=> b.sum - a.sum); // reverse sorted
      if(outliers.incomes.sum > 0){
        earningData.earnings.push(outliers.incomes)
      }
      expensesData.expenses.sort((a,b)=> b.sum - a.sum); // reverse sorted
      if(outliers.outcomes.sum > 0){
        expensesData.expenses.push(outliers.outcomes);
      }
    }
    totalsData = [{direction: 1, category: t`Earnings`, sum: incomes}, {direction: -1, category: t`Expenses`, sum: outcomes}];

    // const chart_colors = {
    //   "1": colors.primary,
    //   "-1": colors.error,
    // }
    const isLargeScreen = useMediaQuery({minWidth: 960 });

    const CustomBarShape = (props) => {
      const { x, y, width, height, fill, barSize } = props;
      // let theX=x, theY=y, theOffsetX=0, theOffsetY=10;
      let radius = [0, 10, 10, 0]; // clockwise, starting from topleft corner
      let theOffsetY = height-barSize, theOffsetX=0;
      let theWidth=width, theHeight=barSize;
      if(isLargeScreen){
        theOffsetY=0;
        theWidth=barSize;
        theHeight=height;
        theOffsetX=(width-barSize)/2;
        radius = [10,10,0,0];
      }
      return <Rectangle x={x+theOffsetX} y={y+theOffsetY} width={theWidth} height={theHeight} fill={fill} radius={radius}></Rectangle>
    };
    const renderCustomisedLabel = (props) => {
      const { x, y, value, height, chartHeight, barSize } = props;
      if(isLargeScreen){
        let trimmedtext = value;
        if(value.length>10){
          trimmedtext = value.slice(0, value.search(/[^a-zA-Z0-9]/))
        }
        return (
          // <text textAnchor="start" alignmentBaseline="middle" transform={`translate(${x+width/2}, ${chartHeight-40}) rotate(270)`}>{trimmedtext}</text>
          <text textAnchor="start" fill={"#666"} alignmentBaseline="middle" transform={`translate(${x}, ${chartHeight-height-40})`}>{trimmedtext}</text>
          // <text x={x} y={y+height} fill={"#666"}>{trimmedtext}</text>
        )
      }else{
        return (
          <text x={x} y={y+height-2*barSize} fill={"#666"} textAnchor="start" dominantBaseline="middle">
            {value}
          </text>
        );
      }
    }
    
    const ResponsiveBarChart = ({data, dataKey, title, label, barClass}) => {
      const defaultLabel = {value:"%", position:"insideTopLeft", offset: 10};
      if(label) {
        label = {...defaultLabel, ...label};
      }else{
        label = defaultLabel;
      }
      const barSize = 8;
      if(isLargeScreen){
        return (
          <>
            <ResponsiveContainer height={400} width={"90%"} >
              <BarChart data={data}
                margin={{top:20, left:0, right:0, bottom:0}}
                barCategoryGap={'15%'} >
                <YAxis type='number' label={label} />
                <XAxis type='category' dataKey="category" 
                  // tick={true} tickLine={false} 
                  tick={false}
                  />
                <Tooltip content={<CustomTooltip />}/>
                <Bar dataKey={dataKey} 
                  className={barClass?? null}
                  // shape={<CustomBarShape barSize={barSize}/>}
                  >
                  {
                    data.map((item, index) => (
                      // <Cell key={`bar_${index}`} fill={item.direction === 1 ? chart_colors["1"]: chart_colors["-1"]} />
                      <Cell key={`bar_${index}`} />
                    ))
                  }
                  <LabelList dataKey="category" content={(props)=>renderCustomisedLabel({...props, chartHeight: 400})} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className='bar-chart-title'>{title}</div>
          </>
        )
      }else{
        const chartHeight = (5*barSize) * (data.length + 1);
        return (
          <>
            <div className='bar-chart-title'>{title}</div>
            <ResponsiveContainer height={chartHeight} width={"100%"} >
              <BarChart data={data}
                layout='vertical'
                margin={{top:10, left:0, right:0, bottom:0}}
                barCategoryGap={"5%"} >
                <XAxis type='number' label={label} axisLine={false} />
                <YAxis type='category' dataKey="category" tick={false} hide={true} />
                <Tooltip content={<CustomTooltip />}/>
                <Bar dataKey={dataKey} shape={<CustomBarShape barSize={barSize} />} activeBar={false} 
                  className={barClass?? null}
                >
                  {
                    data.map((item, index) => (
                      // <Cell key={`bar_${index}`} fill={item.direction === 1 ? chart_colors["1"]: chart_colors["-1"]} />
                      <Cell key={`bar_${index}`} className={item.direction === 1 ? "stats-bar-earnings" : "stats-bar-expenses"} />
                    ))
                  }
                  <LabelList dataKey="category" content={ (props)=> renderCustomisedLabel({...props, barSize:barSize}) } />
                  {/* <LabelList dataKey="category" content={renderCustomisedLabel} /> */}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </>
        )
      }
    };
    
    const nCategories = earningData.earnings.length + expensesData.expenses.length;
    const earningsChartWidth = Math.ceil(10 * earningData.earnings.length / nCategories);
    const expensedChartWidth = Math.floor(10 * expensesData.expenses.length / nCategories);
    return (
      <Row className='mb-2'>
        <Col xs="12" lg={earningsChartWidth}>
          <ResponsiveBarChart barClass="stats-bar-earnings" title={t`Earnings`} data={earningData.earnings}  dataKey={(item)=> 100*item.percent}/>
        </Col>
        <Col xs="12" lg={expensedChartWidth}>
          <ResponsiveBarChart barClass="stats-bar-expenses" title={t`Expenses`} data={expensesData.expenses} dataKey={(item)=> 100*item.percent}/>
        </Col>
        <Col xs="12" lg="2">
          <ResponsiveBarChart barClass="stats-bar-totals" title={t`Totals`} label={{value: "€"}} data={totalsData} dataKey={"sum"}/>
        </Col>
      </Row>
    )
};

export default MovementsStats