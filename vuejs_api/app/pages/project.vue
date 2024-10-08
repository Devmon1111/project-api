<template>
  <v-container>
    <!-- Card for the Header -->
    <v-card class="elevation-3 pa-4 rounded-lg">
      <v-card-title class="bg-light-blue text-dark rounded-t-lg py-3">
        <v-toolbar flat>
          <v-toolbar-title class="font-weight-bold">การตรวจจับ</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn v-if="!isTimeExpired" outlined color="blue" @click="openExamine">ตรวจสอบ</v-btn>
          <v-btn color="red darken-2" outlined @click="goToProjectF">ออก</v-btn>
        </v-toolbar>
      </v-card-title>
    </v-card>

    <!-- Display data in boxes (no table) -->
    <v-row class="mt-4" dense>
      <v-col
        v-for="(item, index) in desserts"
        :key="index"
        cols="12" md="4"
      >
        <v-card class="pa-3 elevation-2">
          <!-- Display image in the card -->
          <v-img
            :src="`/yovle8/${item.image_path}`"
            max-width="120"
            max-height="120"
            class="mx-auto"
          ></v-img>
       <!-- Direction indicator -->
       <v-card-text>
        <div :style="{ color: item.direction === 'IN' ? '#43a047' : 'black', fontWeight: item.direction === 'IN' ? 'bold' : 'normal' }">
        <p>สถานะ: <b>{{ item.direction }}</b></p>  
        </div>
      </v-card-text>
          <!-- Card content -->
          <v-card-title>
            <span class="font-weight-medium">{{ item.name }} </span>
            
          </v-card-title>

      

   

          <!-- Actions: Delete button -->
          <v-card-actions>
            <v-btn class="me-2" small @click="confirmDelete(item)" color="purple">
              ลบ
            </v-btn>
            <v-card-subtitle>
              <span class="text-secondary">{{ formatTimestamp(item.timestamp) }}</span>
            </v-card-subtitle>
          </v-card-actions>
        </v-card>
    
      </v-col>

    </v-row>

    <!-- Schedule Card -->
    <v-card class="mt-6 elevation-2">
      <v-card-title class="bg-grey lighten-4 text-grey darken-3 py-2">
        <span class="font-weight-semibold">เวลา</span>
      </v-card-title>
      <v-card-text>
        <div v-if="schedule">
          <p><v-icon small color="blue">mdi-clock-start</v-icon> <strong>เริ่ม:</strong> {{ formatTimestamp(schedule.start_time) }}</p>
          <p><v-icon small color="blue">mdi-clock-end</v-icon> <strong>สิ้นสุด:</strong> {{ formatTimestamp(schedule.end_time) }}</p>
          <v-alert v-if="isTimeExpired" type="error">สิ้น</v-alert>
          <v-alert v-else type="success">กำลังดำเนินการ</v-alert>
        </div>
        <div v-else>
          <v-skeleton-loader class="my-3" :loading="true"></v-skeleton-loader>
        </div>
      </v-card-text>
    </v-card>

    <!-- Deletion Confirmation Dialog -->
    <v-dialog v-model="dialogDelete" max-width="350px">
      <v-card class="rounded-lg">
        <v-card-title class="text-h6 text-danger">Confirm Deletion</v-card-title>
        <v-card-text>Are you sure you want to delete this entry?</v-card-text>
        <v-card-actions class="justify-end">
          <v-btn color="green" outlined @click="deleteItemConfirm">Yes</v-btn>
          <v-btn color="red" outlined @click="closeDelete">No</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>


<style scoped>
/* Custom styles for a fresher look */
.v-card-title {
  background-color: #e0f7fa !important;
}

.v-card-text {
  font-size: 14px;
}

.v-data-table-header th {
  color: #4a4a4a !important;
}

.v-icon {
  cursor: pointer;
}

.v-alert {
  border-radius: 8px;
}

.text-secondary {
  color: #9e9e9e;
}

.border-light-blue {
  border: 1px solid #80deea;
}
</style>

<script>
import axios from 'axios';
import { format } from 'date-fns';

export default {
  data() {
    return {
      myParam: this.$route.query.myParam || 'default value',
      ids: '',
      dialogDelete: false,
      dialog: false,
      currentImage: '',
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'Name', value: 'name' },
        { text: 'Direction', value: 'direction' },
        { text: 'Timestamp', value: 'timestamp' },
        { text: 'Image', value: 'image_path' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      desserts: [],
      editedIndex: -1,
      editedItem: {},
      defaultItem: {},
      schedule: null,
      isTimeExpired: false,
    };
  },

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? 'Add Data' : 'Edit Data';
    },
  },

  watch: {
    '$route.query.myParam': {
      immediate: true,
      handler(newVal) {
        this.myParam = newVal;
        this.fetchSchedule(); // Fetch schedule when `myParam` changes
      },
    },
    dialogDelete(val) {
      val || this.closeDelete();
    },
  },

  async created() {
    this.initialize();
  },

  methods: {
    async confirmDelete(item) {
      console.log("Confirming delete for ID:", item.id);
      this.ids = item.id;
      this.dialogDelete = true;
    },

    async deleteItemConfirm() {
      if (this.ids) {
        try {
          console.log("Attempting to delete ID:", this.ids);
          const response = await axios.post('http://localhost:9999/delete', { id: this.ids });

          console.log("Delete response:", response.data);
          
          if (response.data.success) {
            await this.loadDesserts();
          } else {
            console.error("Failed to delete the record:", response.data.message);
          }

          this.closeDelete();
        } catch (error) {
          console.error("Error during deletion:", error);
        }
      }
    },

    async openExamine() {
      try {
        const response = await axios.post('http://localhost:9999/open_Examine', { id: this.myParam });
        console.log('Examine file opened with ID:', this.myParam);
      } catch (error) {
        console.error('Error opening file:', error);
      }
    },

    async loadDesserts() {
      try {
        const params = { myParam: this.myParam };
        const response = await axios.get('http://localhost:9999/liststd', { params });
        this.desserts = response.data.data;
        console.log("Loaded desserts:", this.desserts);
      } catch (error) {
        console.error("Error loading desserts:", error);
      }
    },

    async fetchSchedule() {
      try {
        const response = await axios.get(`http://localhost:9999/schedule/${this.myParam}`);
        if (response.data.success) {
          this.schedule = response.data.schedule;
          this.checkTimeExpiry(this.schedule.end_time);
        } else {
          console.error("Failed to fetch schedule:", response.data.message);
        }
      } catch (error) {
        console.error("Error fetching schedule:", error);
      }
    },

    checkTimeExpiry(endTime) {
      const currentTime = new Date();
      const endTimeDate = new Date(endTime);
      this.isTimeExpired = currentTime > endTimeDate;
    },

    initialize() {
      this.loadDesserts();
    },

    closeDelete() {
      this.dialogDelete = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    openDialog(imagePath) {
      // Prepend the correct directory path
      this.currentImage = `/yovle8/${imagePath}`;
      this.dialog = true;
    },

    closeDialog() {
      this.dialog = false;
    },

    formatTimestamp(timestamp) {
      return format(new Date(timestamp), 'yyyy-MM-dd HH:mm:ss');
    },

    goToProjectF() {
      this.$router.push({ path: '/project_f' });
    },
  },
};
</script>
