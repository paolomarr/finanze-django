import Modal from 'react-bootstrap/Modal';
import MovementForm from "./MovementForm";
import { t } from "@lingui/macro";

const MovementModal = ({ showModal, toggleModal, onDataReady, title, fields }) => {
  // const show = showModal.show;
  // const movement = showModal.movement;
  const {show, movement, errors} = showModal;
  if(!title){
    title = showModal.movement ? t`Update movement data` : t`Insert new movement`;
  }
  const innerToggle = () => {
    toggleModal();
  }
  return (
    <Modal show={show} onHide={innerToggle}>
      <Modal.Header closeButton><Modal.Title>{title}</Modal.Title></Modal.Header>
      <Modal.Body>
        <MovementForm movement={movement} cancel={innerToggle} onDataReady={onDataReady} errors={errors} fields={fields}/>
      </Modal.Body>
    </Modal>
  );
};

export default MovementModal;
