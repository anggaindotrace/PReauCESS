import { Component, useState, useRef, useEffect } from '@web/core/Component';
import { useService } from '@web/core/utils/hooks';
import { _t } from '@web/core/l10n';
import { useStore } from '@web/core/store/store';

export class ProductTemplateForm extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.state = useState({
            subjectToMaintenance: this.props.record.subject_to_maintenance,
            tracking: this.props.record.tracking,
            equipmentExists: this.props.record.equipment_id,
        });
        this.equipmentButtonRef = useRef('create_equipment_button');
        this.childEquipmentButtonRef = useRef('create_child_equipment_button');
    }

    async willStart() {
        await this._fetchInitialData();
    }

    async _fetchInitialData() {
        // Fetch initial data if needed
    }

    handleSubjectToMaintenanceChange(event) {
        this.state.subjectToMaintenance = event.target.checked;
        this._updateButtonVisibility();
    }

    handleTrackingChange(event) {
        this.state.tracking = event.target.value;
        this.state.subjectToMaintenance = this.state.tracking === 'serial' ? true : false;
        this._updateButtonVisibility();
    }

    _updateButtonVisibility() {
        if (this.equipmentButtonRef.el) {
            this.equipmentButtonRef.el.style.display = this.state.subjectToMaintenance ? 'block' : 'none';
        }
        if (this.childEquipmentButtonRef.el) {
            this.childEquipmentButtonRef.el.style.display = this.state.equipmentExists ? 'block' : 'none';
        }
    }

    async save() {
        // Save logic here
    }
}

ProductTemplateForm.template = 'product.ProductTemplateForm';
