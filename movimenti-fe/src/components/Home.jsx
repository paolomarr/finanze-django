import MovementsList from "./MovementsList";
import MovementsHistory from "./MovementsHistory";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import fetchMovements from "../queries/fetchMovements";
import { Navigate } from "react-router-dom";
import { t, Trans } from "@lingui/macro"
import TimeSpanSlider from "./TimeSpanSlider";
import { add, sub } from "date-fns";
import { intervalToDuration, min, max } from "date-fns";
import { format, formatDuration } from "../_lib/format_locale"
import { useLingui } from "@lingui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner, faBolt } from "@fortawesome/free-solid-svg-icons";
import FixedBottomRightButton from "./FixedBottomRightButton";
import MovementModal from "./MovementModal"
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from "reactstrap";
import MovementsStats from "./MovementStats";

const generateSlicedData = (data, slice, categories) => {
  const baselineData = data.baseline?? null;
  const minDate = data.minDate;
  const maxDate = data.maxDate;
  const plotStats = {
    chartData: [],
    categories: {},
    listData: [],
    nMovements: function() { return this.chartData.length }, // no arrow function when using 'this'
    minDate: minDate,
    maxDate: maxDate,
    maxCumulative: 0,
    minCumulative: 0,
    incomes: 0,
    outcomes: 0,
    savingRate: function() {return this.outcomes != 0 ? (this.incomes-this.outcomes)/this.incomes : 0},
    duration: function(keys) {
      const fulldur = intervalToDuration({start:this.minDate, end: this.maxDate});
      if(fulldur && keys && keys.length>0){
        const ret = {};
        keys.forEach(key => {
          if(fulldur[key]){
            ret[key] = fulldur[key];
          }
        });
        return ret;
      }
      return fulldur;
    }
  }
  if(baselineData){
    let maxIdx = data.movements.length - 1;
    if(slice){
      plotStats.minDate = max([minDate, slice.minDate]);
      plotStats.maxDate = min([maxDate, slice.maxDate]);
    }
    const baselineVal = baselineData[1];
    let cumulative = baselineVal;
    
    for(let i=maxIdx; i>0; i--){ // remote data comes DATE DESC-sorted, so we start from the last, which is the oldest
      const movement = data.movements[i];
      const mDate = new Date(movement.date);
      cumulative += movement.amount
      plotStats.maxCumulative = Math.max(cumulative, plotStats.maxCumulative);
      plotStats.minCumulative = Math.min(cumulative, plotStats.minCumulative);
      if(mDate < plotStats.minDate) continue;
      if(mDate > plotStats.maxDate) continue;
      plotStats.chartData.push({"date": (mDate).getTime(), "cumulative": cumulative});
      plotStats.listData.push(movement);
      if(movement.amount>0){   
        plotStats.incomes += movement.abs_amount;
      }else {
        plotStats.outcomes += movement.abs_amount;
      }
      const cat = categories.find((cat)=> cat.id === movement.category);
      if(cat){
        if(cat.category in plotStats.categories){
          plotStats.categories[cat.category].sum += movement.abs_amount
        }else{
          plotStats.categories[cat.category] = {...cat, "sum": movement.abs_amount};
        }
      }
    }
  }
  return plotStats;
};
const MovementSummary = ({stats, onSetRange}) => {
  const {i18n} = useLingui();
  const today = new Date();
  const past_year_start = new Date(today.getFullYear() - 1, 0, 1);
  const past_year_end = add(past_year_start, {years:1})
  return (
    <>
    { stats && stats !== undefined ?
      <div className="movement-stats">
        <div className="d-flex flex-row align-items-center justify-content-center my-2">
          <div>{stats.nMovements()} {t`movements in`} {formatDuration(stats.duration(), i18n, ["years", "months", "days"])}</div>
          <UncontrolledDropdown className="px-1">
            <DropdownToggle caret={false} color="">
              <FontAwesomeIcon icon={faBolt} size="lg" className="text-secondary"/>
            </DropdownToggle>
            <DropdownMenu>
              <DropdownItem onClick={() => onSetRange({min: sub(today, {months:3}), max: today})}><Trans>Last 3 months</Trans></DropdownItem>
              <DropdownItem onClick={() => onSetRange({min: sub(today, {months:6}), max: today})}><Trans>Last 6 months</Trans></DropdownItem>
              <DropdownItem onClick={() => onSetRange({min: sub(today, {months:12}), max: today})}><Trans>Last year</Trans></DropdownItem>
              <DropdownItem onClick={() => onSetRange({min: past_year_start, max: past_year_end})}><Trans>Past year</Trans></DropdownItem>
            </DropdownMenu>
          </UncontrolledDropdown>
        </div>
        <div className="movement-stats text-center row justify-content-center my-2">
          <div className="col-12 col-md-3">{t`Outcomes`}: {parseFloat(stats.outcomes).toFixed(2)}€</div>
          <div className="col-12 col-md-3">{t`Incomes`}: {parseFloat(stats.incomes).toFixed(2)}€</div>
          <div className="col-12 col-md-3"><b>{t`Saving rate`}: {parseFloat(stats.savingRate()*100).toFixed(1)}%</b></div>
        </div> 
      </div>: null
    }
    </>
  )
};
const Home = () => {
    const {i18n} = useLingui();
    // const printDate = ((date) => {
    //   return i18n.date(date);
    // });

    const [dataSlice, setDataSlice] = useState(null);
    const [chartData, setChartData] = useState(null);
    const [showModal, setShowModal] = useState({
      movement: null,
      show: false
    });
    const toggleModal = (data_updated) => {
      const show = !showModal.show
      setShowModal({show: show, movement: showModal.movement});
      if(!show && data_updated){
        console.log("Data updated, refreshing...");
        movementResults.refetch();
      }
    };
    const categoryResults = useQuery({
      queryKey: ["categories"],
      queryFn: fetchMovements,
      retry: (failureCount, error) => {
        if(error.message === "forbidden") return false;
        else return 3;
      }, 
    });
    const subcategoryResults = useQuery({
      queryKey: ["subcategories"],
      queryFn: fetchMovements,
      retry: (failureCount, error) => {
        if(error.message === "forbidden") return false;
        else return 3;
      }, 
    });
    const movementResults = useQuery({
      queryKey: ["movements", "all"],
      queryFn: fetchMovements,
      retry: (failureCount, error) => {
        if(error.message === "forbidden") return false;
        else return 3;
      },
      enabled: !!categoryResults.data && !!subcategoryResults.data,
      onSuccess: (data) => {
        setChartData(generateSlicedData(data, dataSlice, categoryResults.data));
      }
    });
    if (movementResults.isLoading) {
      return (
        <div className="loading-pane justify-content-center text-center">
          {/* <h2 className="loader">🌀</h2> */}
          <FontAwesomeIcon icon={faSpinner} spinPulse size="2xl"/>
        </div>
      );
    }
    if (movementResults.isError) {
        switch (movementResults.error.message) {
            case "forbidden":
                console.log("Unable to fetch: unauthenticated");
                return (
                    <Navigate to="/login" />
                )
            default:
                console.log("Unable to fetch: unknown error");
                break;
        }
    }
    const onSliderChange = (changeResult) => {
      if(dataSlice?.minDate == changeResult.minValue && dataSlice?.maxDate == changeResult.maxValue){
        return;
      }
      let newDataSlice = { minDate: changeResult.minValue, maxDate: changeResult.maxValue};
      if(movementResults.data?.movements){
        const minPercent = (changeResult.minValue - changeResult.min) / (changeResult.max - changeResult.min);
        const maxPercent = (changeResult.maxValue - changeResult.min) / (changeResult.max - changeResult.min);
        const movements = movementResults.data.movements;
        const startIdx = parseInt(minPercent * movements.length);
        const endIdx = parseInt(maxPercent * movements.length);
        newDataSlice.minIdx = startIdx;
        newDataSlice.maxIdx = endIdx;
      }
      setDataSlice(newDataSlice);
      setChartData(generateSlicedData(movementResults.data, newDataSlice, categoryResults.data));
    };
    
    const rangeAvail = {
      min: dataSlice?.minDate ?? movementResults.data.minDate,
      max: dataSlice?.maxDate ?? movementResults.data.maxDate,
    }
    return (
      <>
        <h3 className="text-center">
          {t({id: "date.from", message: "From"})} {format(rangeAvail.min, i18n)} 
          {t({id: "date.to", message: "to"})} {format(rangeAvail.max, i18n)}
        </h3>
        <MovementSummary stats={chartData} onSetRange={(range) => onSliderChange({min: rangeAvail.min, max: rangeAvail.min, minValue: range.min, maxValue: range.max})}></MovementSummary>
        <TimeSpanSlider 
          min={new Date(movementResults.data.minDate)} 
          max={new Date(movementResults.data.maxDate)} 
          start={dataSlice?.minDate ?? sub(new Date(), {months:3})} 
          end={dataSlice?.maxDate ?? new Date()} 
          steps={100} 
          onChange={onSliderChange} /> 
        <MovementsHistory data={chartData}/>
        <MovementsStats data={chartData}
        />
        <MovementsList 
          movements={chartData?.listData ?? []}
          categories={categoryResults.data}
          subcategories={subcategoryResults.data}
          onEdit={(movement) => setShowModal({show: true, movement: movement})}/>
        <FixedBottomRightButton onClick={() => setShowModal({show:true, movement: null})} />
        <MovementModal showModal={showModal} toggleModal={toggleModal} title={showModal.movement ? t`Update movement data` : t`Insert new movement`} />
      </>
    )
}

export default Home;