<template>
  <v-container fluid>
    <v-card class="elevation-4 pa-6" style="border-radius: 12px; background-color: #f4f6f9;">
      <v-card-title class="text-primary">
        <v-toolbar flat class="justify-center">
          <v-toolbar-title class="headline font-weight-bold">การตรวจจับ</v-toolbar-title>
          <v-btn color="info" @click="openRegister_Face" class="ml-4" rounded>
            <v-icon left>mdi-face-recognition</v-icon> ลงทะเบียนใบหน้า
          </v-btn>
          <v-btn color="warning" @click="goToSetTime" class="ml-4" rounded>
            <v-icon left>mdi-timer-settings</v-icon> ตั้งเวลา
          </v-btn>
        </v-toolbar>
      </v-card-title>

      <v-data-table
      :headers="headers"
      :items="schedules"
      item-key="id"
      class="elevation-2 mt-5"
      hide-default-footer
    >
        <template v-slot:item="{ item }">
          <tr :class="getRowClass(item)" class="hover-highlight">
            <td>{{ formatTimestamp(item.start_time) }}</td>
            <td>{{ formatTimestamp(item.end_time) }}</td>
            <td>
              <v-btn color="primary" @click="goToProject(item.id)" class="ma-1" rounded outlined>
                <v-icon left>mdi-folder-outline</v-icon> ตรวจสอบ
              </v-btn>
              <v-btn color="red" @click="confirmDeleteSchedule(item.id)" class="ma-1" rounded text>
                <v-icon left>mdi-delete-forever-outline</v-icon> ลบ
              </v-btn>
              <v-chip
                v-if="isBeforeStartTime(item)"
                color="blue"
                class="status-chip white--text"
              >
                <v-icon left>mdi-timer-sand</v-icon> Not Started
              </v-chip>
              <v-chip
                v-else-if="isWithinTime(item)"
                color="green"
                class="status-chip white--text"
              >
                <v-icon left>mdi-timer-outline</v-icon> Active
              </v-chip>
              <v-chip
                v-else
                color="red"
                class="status-chip white--text"
              >
                <v-icon left>mdi-timer-off-outline</v-icon> Expired
              </v-chip>
            </td>
          </tr>
        </template>
      </v-data-table>
    </v-card>

    <!-- Confirmation Dialog -->
    <v-dialog v-model="showConfirmDialog" max-width="500px" transition="dialog-bottom-transition">
      <v-card>
        <v-card-title class="headline">Delete Schedule?</v-card-title>
        <v-card-text class="text-body-1">
          Do you want to remove this schedule? This action cannot be reversed.
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn text @click="cancelDelete">
            <v-icon left>mdi-close</v-icon> Cancel
          </v-btn>
          <v-btn color="red darken-1" @click="deleteScheduleConfirmed">
            <v-icon left>mdi-delete-forever"></v-icon> Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';
import { format } from 'date-fns';

export default {
  data: () => ({
    headers: [
      { text: 'Start Time', value: 'start_time' },
      { text: 'End Time', value: 'end_time' },
      { text: 'Actions', value: 'actions' },
    ],
    schedules: [],
    showConfirmDialog: false,
    scheduleToDelete: null,
  }),

  async created() {
    this.loadSchedules();
  },

  methods: {
    async loadSchedules() {
      try {
        const response = await axios.get('http://localhost:9999/list-schedules');
        this.schedules = response.data.schedules;
      } catch (error) {
        console.error('Error loading schedules:', error);
      }
    },

    formatTimestamp(timestamp) {
      return format(new Date(timestamp), 'dd/MM/yyyy HH:mm');
    },

    isWithinTime(item) {
      const now = new Date();
      return now >= new Date(item.start_time) && now <= new Date(item.end_time);
    },

    isBeforeStartTime(item) {
      const now = new Date();
      return now < new Date(item.start_time);
    },

    getRowClass(item) {
      if (this.isWithinTime(item)) return 'bg-light-green';
      if (this.isBeforeStartTime(item)) return 'bg-light-blue';
      return 'bg-light-red';
    },

    goToSetTime() {
      this.$router.push('/set-time');
    },

    openRegister_Face() {
      this.$router.push('/register');
    },

    goToProject(id) {
      this.$router.push({ path: '/project', query: { myParam: id } });
    },

    confirmDeleteSchedule(id) {
      this.scheduleToDelete = id;
      this.showConfirmDialog = true;
    },

    async deleteScheduleConfirmed() {
      try {
        const deleteResponse = await axios.post('http://localhost:9999/delete-schedule', { id: this.scheduleToDelete });
        if (deleteResponse.data.success) {
          this.loadSchedules();
        }
      } catch (error) {
        console.error('Error deleting schedule:', error);
      }
      this.showConfirmDialog = false;
      this.scheduleToDelete = null;
    },

    cancelDelete() {
      this.showConfirmDialog = false;
      this.scheduleToDelete = null;
    },
  },
};
</script>

<style scoped>
.v-card {
  border-radius: 12px;
  background-color: #fff;
}

.v-toolbar-title {
  font-weight: bold;
  color: #3e4b59;
}

.v-data-table th {
  background-color: #eceff1;
  color: #3e4b59;
}

.bg-light-green {
  background-color: #e8f5e9;
}

.bg-light-blue {
  background-color: #e3f2fd;
}

.bg-light-red {
  background-color: #ffebee;
}

.status-chip {
  font-size: 0.9rem;
  padding: 0 8px;
}

.hover-highlight:hover {
  background-color: #f1f8e9;
}

.v-btn {
  font-size: 0.85rem;
}

.v-dialog {
  border-radius: 12px;
}
</style>
