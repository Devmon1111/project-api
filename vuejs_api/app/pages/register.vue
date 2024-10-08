<template>
  <v-container class="d-flex flex-column align-center justify-center">
    <v-card class="elevation-3 py-6 px-5" style="border-radius: 16px; background-color: #f0f4f7; width: 100%; max-width: 600px;">
      <v-card-title class="d-flex justify-space-between align-center">
        <div class="title text-h5 font-weight-medium">รายชื่อใบหน้า</div>
        <div>
          <v-btn color="primary" class="mx-2" @click="openRegister" rounded>
            <v-icon left>mdi-account-plus</v-icon> ลงทะเบียนใบหน้า
          </v-btn>
          <v-btn color="error" class="mx-2" @click="goToProjectF" rounded>
            <v-icon left>mdi-exit-to-app</v-icon> ออก
          </v-btn>
        </div>
      </v-card-title>
      
      <v-divider></v-divider>

      <v-card-text class="d-flex flex-column align-center mt-4">
        <template v-for="item in staffs" :key="item.id">
          <v-card class="mb-3" style="width: 100%; border-radius: 12px; background-color: #ffffff; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
            <v-card-title class="d-flex align-center">
              <v-avatar size="60">
                <img :src="`/yovle8/${item.face_img}`" alt="Face Image" style="width: 75%; height: 75%; object-fit: cover;" />
              </v-avatar>
              
              <div class="flex-grow-1">
                <div class="text-body-1 font-weight-bold"><b><p>ชื่อ: {{ item.displayName }}</p></b></div>
                <div class="text-body-2 text-muted"><p><b>เเผนก: {{ item.dept }}</b></p></div>
              </div>
              <v-btn icon @click="deleteItem(item)" color="error">
                <v-icon>mdi-trash-can-outline</v-icon>
              </v-btn>
            </v-card-title>
          </v-card>
        </template>

        <template v-if="staffs.length === 0">
          <v-card class="text-center">
            <v-card-text class="text-body-2 text-muted">
              ไม่มีข้อมูลสมาชิก <v-btn color="primary" @click="initialize">Refresh</v-btn>
            </v-card-text>
          </v-card>
        </template>
      </v-card-text>

      <!-- Delete Confirmation Dialog -->
      <v-dialog v-model="dialogDelete" max-width="450px">
        <v-card>
          <v-card-title class="text-h6 font-weight-bold">Confirm Deletion</v-card-title>
          <v-card-text class="text-body-1">
            Are you sure you want to delete this member? This action cannot be undone.
          </v-card-text>
          <v-card-actions class="d-flex justify-end">
            <v-btn color="info" text @click="closeDelete">
              <v-icon left>mdi-cancel</v-icon> Cancel
            </v-btn>
            <v-btn color="error" text @click="deleteItemConfirm">
              <v-icon left>mdi-delete</v-icon> Delete
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </v-container>
</template>

<style scoped>
.v-card {
  border-radius: 16px;
  background-color: #f0f4f7;
}

.v-card-title {
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.v-btn {
  border-radius: 12px;
  font-size: 0.9rem;
}

.v-avatar img {
  border-radius: 10%;
}

.text-body-1 {
  font-size: 1rem;
}
</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      dialogDelete: false,
      currentItem: null,
      headers: [
        { text: 'Name', value: 'displayName', align: 'start' },
        { text: 'Department', value: 'dept' },
        { text: 'Face Image', value: 'face_img', sortable: false },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      staffs: [],
    };
  },

  created() {
    this.initialize();
  },

  methods: {
    async fetchStaffs() {
      try {
        const response = await axios.get('http://localhost:9999/liststaffs');
        if (response.data.ok) {
          this.staffs = response.data.students;
        } else {
          console.error('Error fetching staff data:', response.data);
        }
      } catch (error) {
        console.error('Error fetching staff data:', error);
      }
    },

    deleteItem(item) {
      this.currentItem = item;
      this.dialogDelete = true;
    },

    async deleteItemConfirm() {
      if (this.currentItem) {
        try {
          const response = await axios.post('http://localhost:9999/delete_face', { id: this.currentItem.id });
          if (response.data.success) {
            this.initialize();
          } else {
            console.error("Failed to delete the record:", response.data.message);
          }
        } catch (error) {
          console.error("Error during deletion:", error);
        }
      }
      this.closeDelete();
    },

    closeDelete() {
      this.dialogDelete = false;
      this.currentItem = null;
    },

    async openRegister() {
      try {
        await axios.post('http://localhost:9999/open_register');
      } catch (error) {
        console.error('Error opening file:', error);
      }
    },
    
    goToProjectF() {
      this.$router.push({ path: '/project_f' });
    },

    initialize() {
      this.fetchStaffs();
    }
  }
};
</script>

<style scoped>
.v-card {
  border-radius: 16px;
  background-color: #f0f4f7;
}

.v-card-title {
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.v-btn {
  border-radius: 12px;
  font-size: 0.9rem;
}

.v-data-table {
  border-radius: 12px;
}

.v-avatar img {
  border-radius: 10%;
}

.text-body-1 {
  font-size: 1rem;
}

.v-dialog .v-card {
  border-radius: 12px;
}
</style>
