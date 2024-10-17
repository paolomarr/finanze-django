import Modal from 'react-bootstrap/Modal';
import MovementForm from "./MovementForm";
import { t } from "@lingui/macro";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPenToSquare } from "@fortawesome/free-regular-svg-icons";
import { faCamera, faUpload, faXmark, faCircle } from '@fortawesome/free-solid-svg-icons';
import { useState } from 'react';
import { useRef } from 'react';
import { useCallback } from 'react';
import Webcam from 'react-webcam';
import ToggleButton from 'react-bootstrap/esm/Button';
import Button from 'react-bootstrap/esm/Button';

const WebcamComponent = () => {
  const webcamRef = useRef(null);
  const [imgSrc, setImgSrc] = useState(null);
  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImgSrc(imageSrc);
  }, [webcamRef, setImgSrc]);
  return (
    <>
      { imgSrc ? 
        <div className='position-relative'>
          <img src={imgSrc} alt='The shot you take'/> 
          <div className='position-absolute bottom-0 start-50 opacity-75 translate-middle'>
            <Button className='mx-1' variant='secondary' onClick={() => setImgSrc(null)}><FontAwesomeIcon icon={faXmark} /></Button>
            <Button className='mx-1' variant='success'><FontAwesomeIcon icon={faUpload} /></Button>
          </div>
        </div>
      :
      <div className='position-relative'>
        <Webcam className='w-100'
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
        />
        <FontAwesomeIcon className='position-absolute bottom-0 start-50 translate-middle opacity-75' 
          icon={faCircle} 
          size="2xl" 
          style={{"color": "#f25a50"}}
          onClick={capture}/>
      </div>
      }
    </>
  )
}
const MovementModal = ({ showModal, toggleModal, onDataReady, title, fields }) => {
  const {show, movement, errors} = showModal;
  if(!title){
    title = showModal.movement ? t`Update movement data` : t`Insert new movement`;
  }
  const [showCamera, setShowCamera] = useState(false);
  const innerToggle = () => {
    setShowCamera(false);
    toggleModal();
  };
  const imageMutation = useMutation({
    mutationFn: mutateReceipt,
    // TODO: handle errors and response
    onSuccess: (result) => {
      console.log(result);
    },
  });
  const sendImage = (imgdata) => {
    imageMutation.mutate(imgdata);
  }
  return (
    <Modal show={show} onHide={innerToggle}>
      <Modal.Header closeButton><Modal.Title>{title}</Modal.Title></Modal.Header>
      <Modal.Body>
        <div style={{"textAlign": "center"}} className='mb-2'>
          <ToggleButton type='checkbox' className='mx-2' variant="outline-secondary" value="1" checked={!showCamera}><FontAwesomeIcon icon={faPenToSquare} onClick={() => setShowCamera(false)}/></ToggleButton>
          <ToggleButton type='checkbox' className='mx-2' variant="outline-secondary" value="1" checked={showCamera}><FontAwesomeIcon icon={faCamera} onClick={() => setShowCamera(true)}/></ToggleButton>
        </div>
        { showCamera ? 
          <WebcamComponent /> :
          <MovementForm movement={movement} cancel={innerToggle} onDataReady={onDataReady} errors={errors} fields={fields}/>
        }
      </Modal.Body>
    </Modal>
  );
};

export default MovementModal;
