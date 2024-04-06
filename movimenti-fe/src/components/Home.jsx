import MovementsList from "./MovementsList";
import MovementsHistory from "./MovementsHistory";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import fetchMovements from "../queries/fetchMovements";
import { Navigate } from "react-router-dom";
import { t, Trans } from "@lingui/macro"
import TimeSpanSlider from "./TimeSpanSlider";
import { add, sub } from "date-fns";
import { intervalToDuration} from "date-fns";
import { format, formatDuration } from "../_lib/format_locale"
import { useLingui } from "@lingui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner, faBolt } from "@fortawesome/free-solid-svg-icons";
import FixedBottomRightButton from "./FixedBottomRightButton";
import MovementModal from "./MovementModal"
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from "reactstrap";
import MovementsStats from "./MovementStats";


const MovementSummary = ({data, slice, onSetRange}) => {
  const {i18n} = useLingui();
  const today = new Date();
  const past_year_start = new Date(today.getFullYear() - 1, 0, 1);
  const past_year_end = add(past_year_start, {years:1});
  let outcomes = 0;
  let incomes = 0;
  let nMovements = 0;
  let minDate = today;
  let maxDate = 0;
  if(data){
    for (const movement of data.movements) {
      const mDate = new Date(movement.date);
      if(slice){
        if(mDate < slice.minDate || mDate > slice.maxDate){
          continue;
        }
      }
      minDate = Math.min(minDate, mDate);
      maxDate = Math.max(maxDate, mDate);
      nMovements+=1;
      if(movement.amount > 0){
        incomes += movement.abs_amount;
      }else if(movement.amount < 0){
        outcomes += movement.abs_amount;
      }
    }
  }
  const savingRate = incomes>0 ? (incomes-outcomes)/incomes : 0;
  let duration = intervalToDuration({start:minDate, end: maxDate});
  ["years", "months", "days"].forEach((key) => {
    if(!duration[key] || duration.key<=0){
      delete duration.key;
    }
  });
  return (
    <>
      <div className="movement-stats">
        <div className="d-flex flex-row align-items-center justify-content-center my-2">
          <div>{nMovements} {t`movements in`} {formatDuration(duration, i18n, ["years", "months", "days"])}</div>
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
          <div className="col-12 col-md-3">{t`Outcomes`}: {parseFloat(outcomes).toFixed(2)}€</div>
          <div className="col-12 col-md-3">{t`Incomes`}: {parseFloat(incomes).toFixed(2)}€</div>
          <div className="col-12 col-md-3"><b>{t`Saving rate`}: {parseFloat(savingRate*100).toFixed(1)}%</b></div>
        </div> 
      </div>
    </>
  )
};
const Home = () => {
    const {i18n} = useLingui();

    const [dataSlice, setDataSlice] = useState({
      minDate: sub(new Date(), {months:3}),
      maxDate: new Date(),
    });
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
    const reverseDataMovements = (data) => {
      let ascMovements = data.movements?.toReversed(); // reversed because movements come date desc-ordered
      return {...data, movements: ascMovements};
    };
    const movementResults = useQuery({
      queryKey: ["movements", "all"],
      queryFn: fetchMovements,
      retry: (failureCount, error) => {
        if(error.message === "forbidden") return false;
        else return 3;
      },
      enabled: !!categoryResults.data && !!subcategoryResults.data,
      select: reverseDataMovements,
    });
    
    if (movementResults.isLoading) {
      return (
        <div className="loading-pane justify-content-center text-center">
          <FontAwesomeIcon icon={faSpinner} spinPulse size="2xl"/>
        </div>
      );
    }
    if (movementResults.isError) {
        switch (movementResults.error.message) {
            case "forbidden":
                console.log("Unable to fetch: unauthenticated");
                break;
            default:
                console.log("Unable to fetch: unknown error");
                break;
        }
        return (
            <Navigate to="/login" />
        )
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
    };
    
    return (
      <>
        <h3 className="text-center">
          {t({id: "date.from", message: "From"})} {format(dataSlice.minDate, i18n)} 
          {t({id: "date.to", message: "to"})} {format(dataSlice.maxDate, i18n)}
        </h3>
        <MovementSummary data={movementResults.data} slice={dataSlice} onSetRange={(range) => onSliderChange({min: dataSlice.minDate, max: dataSlice.maxDate, minValue: range.min, maxValue: range.max})}></MovementSummary>
        <TimeSpanSlider 
          min={new Date(movementResults.data.minDate)} 
          max={new Date(movementResults.data.maxDate)} 
          start={dataSlice.minDate} 
          end={dataSlice.maxDate} 
          steps={100} 
          onChange={onSliderChange} /> 
        <MovementsHistory data={movementResults.data} slice={dataSlice}/>
        <MovementsStats data={movementResults.data} categories={categoryResults.data} slice={dataSlice}
        />
        <MovementsList 
          movements={movementResults.data.movements}
          slice={dataSlice}
          categories={categoryResults.data}
          subcategories={subcategoryResults.data}
          onEdit={(movement) => setShowModal({show: true, movement: movement})}/>
        <FixedBottomRightButton onClick={() => setShowModal({show:true, movement: null})} />
        <MovementModal showModal={showModal} toggleModal={toggleModal} title={showModal.movement ? t`Update movement data` : t`Insert new movement`} />
      </>
    )
}

export default Home;