import { useState } from 'react';
import MultiRangeSlider from "multi-range-slider-react";
import { format, eachMonthOfInterval, eachWeekOfInterval, eachDayOfInterval, intervalToDuration } from 'date-fns' 


const TimeSpanSlider = ({min, max, start, end, steps, onChange}) => {

    const nSteps = steps;
    const [step] = useState((end - start)/nSteps);

    const initialInterval = {start: min, end: max};
    const initialDuration = intervalToDuration(initialInterval);
    let eachFunction = null;
    let formatPattern = "P";
    if(initialDuration.years > 0){
      eachFunction = eachMonthOfInterval;
      formatPattern = "MMM yyyy";
    }else if(initialDuration.months > 0){
      eachFunction = eachWeekOfInterval;
      formatPattern = "dd MMM yyyy";
    }else{
      eachFunction = eachDayOfInterval;
      formatPattern = "dd MMM";
    }
    let _labels = eachFunction(initialInterval).map((date)=>{return format(date, formatPattern);});
    let labels;
    const multiples = parseInt(_labels.length/10);
    if(multiples>1){ // 20 or more
      labels = _labels.filter((label, index)=> index % multiples == 0 );
    }else{
      labels = _labels;
    }
    const [currentChange, setCurrentChange] = useState({min: min, max: max, minValue: start, maxValue: end});

    const handleInput = (changeResult) => {
      if(changeResult.minValue != currentChange.minValue || changeResult.maxValue != currentChange.maxValue)
        setCurrentChange(changeResult);
        onChange? onChange(changeResult) : null;
    };

    return <MultiRangeSlider 
              min={min}
              max={max}
              step={step}
              minValue={currentChange.minValue}
              maxValue={currentChange.maxValue}
              minCaption={format(currentChange.minValue, "P")}
              maxCaption={format(currentChange.maxValue, "P")}
              ruler={false}
              onInput={(e)=>{
                handleInput(e);
              }}
              labels={labels}
            />
};

export default TimeSpanSlider
