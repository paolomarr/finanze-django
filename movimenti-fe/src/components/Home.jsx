import MovementsList from "./MovementsList";
import MovementsHistory from "./MovementsHistory";
import { useState } from "react";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import fetchMovements from "../queries/fetchMovements";
import mutateMovement from "../queries/mutateMovement";
import { Navigate, useNavigate } from "react-router-dom";
import { msg, t } from "@lingui/macro"
import { Trans } from "@lingui/react";
import TimeSpanSlider from "./TimeSpanSlider";
import { interval, add, sub, startOfMonth, startOfYear, endOfYear } from "date-fns";
import { intervalToDuration} from "date-fns";
import { format, formatDuration } from "../_lib/format_locale"
import { useLingui } from "@lingui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBolt } from "@fortawesome/free-solid-svg-icons";
import FixedBottomRightButton from "./FixedBottomRightButton";
import MovementModal from "./MovementModal"
import Dropdown from 'react-bootstrap/Dropdown';
import MovementsStats from "./MovementStats";
import {forwardRef} from "react";
import LoadingDiv from "./LoadingDiv";

// The forwardRef is important!!
// Dropdown needs access to the DOM node in order to position the Menu
const CustomToggle = forwardRef(function CustomToggle({ children, onClick }, ref){
  return (
    <button
      className="border-0 bg-transparent"
      ref={ref}
      onClick={(e) => {
        e.preventDefault();
        onClick(e);
      }}
    >
      {children}
    </button>
  )
});
const CustomRanges = {
  currentMonth: {range: {min: startOfMonth(new Date()), max: new Date()}, name: msg`Current month`},
  last3: {range: {min: sub(new Date(), {months:3}), max: new Date()}, name: msg`Last 3 months`},
  last6: {range: {min: sub(new Date(), {months:6}), max: new Date()}, name: msg`Last 6 months`},
  last12: {range: {min: sub(new Date(), {months:12}), max: new Date()}, name: msg`Last year`},
  pastYear: {range: {min: startOfYear(sub(new Date(), {years:1})), max: endOfYear(sub(new Date(), {years:1}))}, name: msg`Past year`},
};
const MovementSummary = ({data, onSetRange}) => {
  const {i18n} = useLingui();
  let outcomes = 0;
  let incomes = 0;
  let nMovements = 0;
  let minDate = new Date(data?.filtered.minDate);
  let maxDate = new Date(data?.filtered.maxDate);
  if(data?.filtered?.movements){
    for (const movement of data.filtered.movements) {
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
          <Dropdown className="px-1">
            <Dropdown.Toggle variant="outline-secondary" as={CustomToggle}>
              <FontAwesomeIcon icon={faBolt} size="lg" className="text-secondary"/>
            </Dropdown.Toggle>
            <Dropdown.Menu>
              { Object.keys(CustomRanges).map((rangeKey)=> {
                const range = CustomRanges[rangeKey];
                return <Dropdown.Item key={rangeKey} onClick={() => onSetRange(range.range)}><Trans id={range.name.id} /></Dropdown.Item>
                })
              }
            </Dropdown.Menu>
          </Dropdown>
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
    const queryclient = useQueryClient();
    const navigate = useNavigate();

    const persistedDataSliceStringyfied = localStorage.getItem("Home.dataSliceSpanDuration");
    let persistedDuration = null;
    if(persistedDataSliceStringyfied){
      persistedDuration = JSON.parse(persistedDataSliceStringyfied);
    }
    const [dataSlice, setDataSlice] = useState({
      minDate: persistedDuration ? sub(new Date(), persistedDuration) : sub(new Date(), {months:3}),
      maxDate: new Date(),
    });
    const [showModal, setShowModal] = useState({
      movement: null,
      show: false,
      errors: null,
    });
    const toggleModal = () => {
      const show = !showModal.show;
      setShowModal({...showModal, show: show});
    };
    const categoryResults = useQuery({
      queryKey: ["categories"],
      queryFn: fetchMovements,
      retry: (failureCount, error) => {
        if(error.message === "forbidden"){
          queryclient.cancelQueries();
          navigate("/login");
          return false;
        } else{ 
          return failureCount-1;
        }
      }, 
    });
    const subcategoryResults = useQuery({
      queryKey: ["subcategories"],
      queryFn: fetchMovements,
      retry: (failureCount, error) => {
        if(error.message === "forbidden"){
          queryclient.cancelQueries();
          navigate("/login");
          return false;
        } else{ 
          return failureCount-1;
        }
      }, 
    });
    // const reverseDataMovements = (data) => {
    //   let ascMovements = data.filtered.movements?.toSorted((a,b)=> a.date>b.date ? 1 : -1); // reversed because movements come date desc-ordered
    //   return {...data, filtered: {...data.filtered, movements: ascMovements}};
    // };
    const movementResults = useQuery({
      queryKey: ["movements", {
        all: true, 
        datefrom: dataSlice.minDate, 
        dateto: add(dataSlice.maxDate, {days: 1}), // add one day to include the last day
        sort_field: "date",
      }],
      queryFn: fetchMovements,
      retry: (failureCount, error) => {
        if(error.message === "forbidden"){
          queryclient.cancelQueries();
          navigate("/login");
          return false;
        } else{ 
          console.log(`'movements query error: ${error.message}`);
          return failureCount-1;
        }
      },
      enabled: !!categoryResults.data && !!subcategoryResults.data,
      // select: reverseDataMovements,
    });
    const mutation = useMutation({
      mutationFn: ({movement, _delete}) => {
        setShowModal({...showModal, errors: null});
        return mutateMovement({movement, _delete});
      },
      onSuccess: (result, {_continue}) => {
      // onSuccess: (result, {movement, _delete, _continue}) => {
        // remove movement from showModal object
        setShowModal({...showModal, show: _continue, movement: null, errors: {}})
        queryclient.invalidateQueries(["movements"]);
        // // update data
        // queryclient.setQueriesData(["movements"], (oldData) => {
        //   if(_delete){ // it's been a DELETE
        //     const index = oldData.filtered.movements.findIndex((omovement)=> omovement.id === movement.id);
        //     if(index>=0){
        //       oldData.filtered.movements.splice(index, 1);
        //       return oldData;
        //     }
        //   }else if(movement.id){ // it's been a PUT
        //     const index = oldData.filtered.movements.findIndex((omovement)=> omovement.id === movement.id);
        //     if(index>=0){
        //       oldData.filtered.movements.splice(index, 1, result);
        //       return oldData;
        //     }  
        //   }else{ // it's been a POST
        //     oldData.filtered.movements.push(result);
        //     // return reverseDataMovements(oldData);
        //     return oldData;
        //   }
        // });
      },
      onError: (error, variables, context) => {
        console.log(variables);
        console.log(context);
        setShowModal({...showModal, errors: error.cause})
      }
    });
    
    if (movementResults.isLoading) {
      return <LoadingDiv />
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
      const newDataSlice = { minDate: changeResult.minValue, maxDate: changeResult.maxValue};
      const durationToPersist = intervalToDuration(new interval(newDataSlice.minDate, newDataSlice.maxDate));
      localStorage.setItem("Home.dataSliceSpanDuration", JSON.stringify(durationToPersist));
      setDataSlice(newDataSlice);
    };
    
    return (
      <>
        <h3 className="text-center">
          {t({id: "date.from", message: "From"})} {format(dataSlice.minDate, i18n)}{' '} 
          {t({id: "date.to", message: "to"})} {format(dataSlice.maxDate, i18n)}
        </h3>
        <MovementSummary data={movementResults.data} slice={dataSlice} onSetRange={(range) => onSliderChange({min: dataSlice.minDate, max: dataSlice.maxDate, minValue: range.min, maxValue: range.max})}></MovementSummary>
        <TimeSpanSlider 
          min={new Date(movementResults.data.alltime.minDate)} 
          max={new Date(movementResults.data.alltime.maxDate)} 
          start={dataSlice.minDate} 
          end={dataSlice.maxDate} 
          steps={100} 
          onChange={onSliderChange} /> 
        <MovementsHistory data={movementResults.data} slice={dataSlice} categories={categoryResults.data}/>
        <MovementsStats data={movementResults.data} categories={categoryResults.data} slice={dataSlice}
        />
        <MovementsList 
          movements={movementResults.data.filtered.movements}
          // slice={dataSlice}
          categories={categoryResults.data}
          subcategories={subcategoryResults.data}
          onEdit={(movement) => setShowModal({show: true, movement: movement})}/>
        <FixedBottomRightButton onClick={() => setShowModal({show:true, movement: null})} />
        <MovementModal 
          showModal={showModal}
          onMovementUpdate={(newMovement)=>setShowModal({...showModal, movement:newMovement})}
          toggleModal={toggleModal} 
          onDataReady={(movement, todelete, tocontinue) => mutation.mutate({movement: movement, _delete: todelete, _continue: tocontinue})} />
      </>
    )
}

export default Home;